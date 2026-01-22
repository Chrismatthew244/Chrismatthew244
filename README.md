# Telegram Live Dashboard (Userbot)

A local web dashboard that monitors up to 4 Telegram channels in real time, translates messages to Danish, highlights keyword alerts, and keeps an alert history.

## Features
- **Live multi-channel feed** with 2–4 columns that auto-resize based on active slots.
- **On-the-fly channel switching** by username or invite link.
- **Danish translation** via `deep_translator` for every incoming message.
- **Keyword alerting** with glowing red cards + audible notifications.
- **Alert history** to review triggered keyword matches.

## Requirements
- Python 3.10+
- A Telegram API ID + API HASH (from https://my.telegram.org)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Setup
Create a `.env` file in the project root:

```bash
API_ID=123456
API_HASH=your_api_hash_here
# Optional: change the session file name
SESSION_NAME=telegram_dashboard
```

## Run the App

```bash
uvicorn main:app --reload
```

Visit: `http://127.0.0.1:8000`

## Translation Settings
Open the settings menu (top-right gear icon) to:
- Choose the translation provider (Google or DeepL).
- Set the target translation language (default: Danish `da`).
- Enter your DeepL API key and monitor usage if DeepL is selected.

> **Note:** On first run, Telethon may prompt you to authenticate your Telegram account in the terminal. Complete the login to generate the session file.
