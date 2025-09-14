from fastapi import Depends, FastAPI

from core import auth
from core.auth import Token, User
from customers.router import router as customers_router
from tasks.router import router as tasks_router
from billing.router import router as billing_router
from documents.router import router as documents_router


app = FastAPI()

app.include_router(customers_router)
app.include_router(tasks_router)
app.include_router(billing_router)
app.include_router(documents_router)


@app.post("/token", response_model=Token)
async def login(form_data: auth.OAuth2PasswordRequestForm = Depends()):
    return await auth.login(form_data)


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return current_user
