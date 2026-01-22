import asyncio
import logging
import os
from typing import Dict, Optional, Set, Tuple

import requests
from deep_translator import DeeplTranslator, GoogleTranslator
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from telethon import TelegramClient, events

load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "telegram_dashboard")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_dashboard")

app = FastAPI()
templates = Jinja2Templates(directory="templates")


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: Set[WebSocket] = set()
        self.lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self.lock:
            self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self.lock:
            self.active_connections.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        async with self.lock:
            connections = list(self.active_connections)
        for connection in connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                await self.disconnect(connection)


class DashboardState:
    def __init__(self) -> None:
        self.slot_to_chat_id: Dict[int, int] = {}
        self.slot_to_title: Dict[int, str] = {}
        self.chat_id_to_slot: Dict[int, int] = {}
        self.keywords: Set[str] = set()
        self.translation_provider = "google"
        self.target_language = "da"
        self.deepl_api_key: Optional[str] = None
        self.deepl_usage: Optional[dict] = None
        self.lock = asyncio.Lock()

    async def set_keywords(self, keywords: Set[str]) -> None:
        async with self.lock:
            self.keywords = keywords

    async def set_translation_settings(
        self,
        provider: str,
        target_language: str,
        deepl_api_key: Optional[str],
        deepl_usage: Optional[dict],
    ) -> None:
        async with self.lock:
            self.translation_provider = provider
            self.target_language = target_language
            if deepl_api_key is not None:
                self.deepl_api_key = deepl_api_key
            self.deepl_usage = deepl_usage

    async def assign_slot(self, slot: int, chat_id: int, title: str) -> None:
        async with self.lock:
            previous_chat_id = self.slot_to_chat_id.get(slot)
            if previous_chat_id:
                self.chat_id_to_slot.pop(previous_chat_id, None)
            self.slot_to_chat_id[slot] = chat_id
            self.slot_to_title[slot] = title
            self.chat_id_to_slot[chat_id] = slot

    async def clear_slot(self, slot: int) -> None:
        async with self.lock:
            previous_chat_id = self.slot_to_chat_id.pop(slot, None)
            if previous_chat_id:
                self.chat_id_to_slot.pop(previous_chat_id, None)
            self.slot_to_title.pop(slot, None)

    async def get_slot_for_chat(self, chat_id: int) -> Optional[int]:
        async with self.lock:
            return self.chat_id_to_slot.get(chat_id)

    async def get_state_snapshot(self) -> dict:
        async with self.lock:
            return {
                "slots": {
                    str(slot): {
                        "chat_id": chat_id,
                        "title": self.slot_to_title.get(slot),
                    }
                    for slot, chat_id in self.slot_to_chat_id.items()
                },
                "keywords": sorted(self.keywords),
                "translation": {
                    "provider": self.translation_provider,
                    "target_language": self.target_language,
                    "deepl_usage": self.deepl_usage,
                },
            }

    async def find_keyword(self, text: str) -> Optional[str]:
        async with self.lock:
            keywords = list(self.keywords)
        lowered = text.lower()
        for keyword in keywords:
            if keyword and keyword.lower() in lowered:
                return keyword
        return None

    async def get_translation_settings(self) -> dict:
        async with self.lock:
            return {
                "provider": self.translation_provider,
                "target_language": self.target_language,
                "deepl_api_key": self.deepl_api_key,
            }


manager = WebSocketManager()
state = DashboardState()
telegram_client: Optional[TelegramClient] = None
translator_cache: Dict[Tuple[str, str, Optional[str]], object] = {}


def get_translator(provider: str, target_language: str, api_key: Optional[str]) -> object:
    cache_key = (provider, target_language, api_key)
    if cache_key in translator_cache:
        return translator_cache[cache_key]
    if provider == "deepl" and api_key:
        translator_instance = DeeplTranslator(
            api_key=api_key,
            source="auto",
            target=target_language,
        )
    else:
        translator_instance = GoogleTranslator(source="auto", target=target_language)
    translator_cache[cache_key] = translator_instance
    return translator_instance


async def fetch_deepl_usage(api_key: str) -> Optional[dict]:
    if not api_key:
        return None
    base_url = "https://api-free.deepl.com/v2/usage"
    if not api_key.endswith(":fx"):
        base_url = "https://api.deepl.com/v2/usage"

    def _request_usage() -> dict:
        response = requests.get(
            base_url,
            headers={"Authorization": f"DeepL-Auth-Key {api_key}"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    try:
        return await asyncio.to_thread(_request_usage)
    except Exception as exc:
        logger.warning("DeepL usage request failed: %s", exc)
        return None


async def translate_text(text: str) -> str:
    if not text:
        return ""
    try:
        settings = await state.get_translation_settings()
        provider = settings["provider"]
        target_language = settings["target_language"]
        api_key = settings.get("deepl_api_key")
        if provider == "deepl" and not api_key:
            return text
        translator_instance = get_translator(provider, target_language, api_key)
        return await asyncio.to_thread(translator_instance.translate, text)
    except Exception as exc:
        logger.warning("Translation failed: %s", exc)
        return text


async def resolve_channel(identifier: str) -> dict:
    if telegram_client is None:
        raise RuntimeError("Telegram client not initialized")
    entity = await telegram_client.get_entity(identifier)
    title = getattr(entity, "title", None) or getattr(entity, "username", None) or str(entity)
    chat_id = entity.id
    return {"title": title, "chat_id": chat_id}


@app.on_event("startup")
async def startup_event() -> None:
    global telegram_client
    if not API_ID or not API_HASH:
        logger.warning("API_ID or API_HASH missing; Telegram client will not start.")
        return
    telegram_client = TelegramClient(SESSION_NAME, int(API_ID), API_HASH)
    await telegram_client.start()

    @telegram_client.on(events.NewMessage)
    async def handle_new_message(event: events.NewMessage.Event) -> None:
        if event.chat_id is None:
            return
        slot = await state.get_slot_for_chat(event.chat_id)
        if slot is None:
            return
        original_text = event.message.message or ""
        translated_text = await translate_text(original_text)
        sender = "Unknown"
        if event.chat is not None:
            sender = getattr(event.chat, "title", None) or getattr(event.chat, "username", None) or "Unknown"
        timestamp = event.message.date.isoformat()
        keyword = await state.find_keyword(f"{original_text} {translated_text}")
        is_alert = keyword is not None
        await manager.broadcast(
            {
                "type": "message",
                "slot": slot,
                "timestamp": timestamp,
                "sender": sender,
                "translated_text": translated_text,
                "original_text": original_text,
                "is_alert": is_alert,
                "keyword": keyword,
            }
        )


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if telegram_client is not None:
        await telegram_client.disconnect()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        await websocket.send_json({"type": "init", **(await state.get_state_snapshot())})
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            if message_type == "set_keywords":
                keywords = {
                    keyword.strip()
                    for keyword in data.get("keywords", [])
                    if keyword and keyword.strip()
                }
                await state.set_keywords(keywords)
                await manager.broadcast({"type": "keywords", "keywords": sorted(keywords)})
            elif message_type == "set_translation":
                provider = (data.get("provider") or "google").lower()
                target_language = (data.get("target_language") or "da").lower()
                deepl_api_key = data.get("deepl_api_key")
                deepl_usage = None
                if provider == "deepl" and deepl_api_key:
                    deepl_usage = await fetch_deepl_usage(deepl_api_key)
                await state.set_translation_settings(
                    provider=provider,
                    target_language=target_language,
                    deepl_api_key=deepl_api_key,
                    deepl_usage=deepl_usage,
                )
                await manager.broadcast(
                    {
                        "type": "translation_settings",
                        "provider": provider,
                        "target_language": target_language,
                        "deepl_usage": deepl_usage,
                    }
                )
            elif message_type == "load_channel":
                slot = int(data.get("slot"))
                identifier = (data.get("identifier") or "").strip()
                if not identifier:
                    await state.clear_slot(slot)
                    await manager.broadcast({"type": "slot_cleared", "slot": slot})
                    continue
                try:
                    channel_info = await resolve_channel(identifier)
                    await state.assign_slot(slot, channel_info["chat_id"], channel_info["title"])
                    await manager.broadcast(
                        {
                            "type": "slot_loaded",
                            "slot": slot,
                            "title": channel_info["title"],
                            "identifier": identifier,
                        }
                    )
                except Exception as exc:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "message": f"Failed to load channel: {exc}",
                            "slot": slot,
                        }
                    )
            else:
                await websocket.send_json({"type": "error", "message": "Unknown command"})
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as exc:
        logger.error("WebSocket error: %s", exc)
        await manager.disconnect(websocket)
