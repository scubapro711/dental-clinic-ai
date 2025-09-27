from fastapi import APIRouter, Request
from .webhooks import whatsapp_webhook, telegram_webhook

router = APIRouter()

@router.post("/whatsapp")
async def handle_whatsapp(request: Request):
    data = await request.json()
    return await whatsapp_webhook(data)

@router.post("/telegram")
async def handle_telegram(request: Request):
    data = await request.json()
    return await telegram_webhook(data)

