# Telegram Bot - Quick Start

## ⚡ 5-Minute Setup

### 1. Create Bot
```
1. Open Telegram → Search @BotFather
2. Send: /newbot
3. Name: DentaFlow Assistant
4. Username: dentaflow_bot
5. Copy token: 123456789:ABCdef...
```

### 2. Configure
```bash
# Add to .env
echo "TELEGRAM_BOT_TOKEN=your-token-here" >> .env
echo "TELEGRAM_WEBHOOK_URL=https://dentaflow.ai/api/v1/telegram/webhook" >> .env
```

### 3. Setup Webhook
```bash
cd backend
python3 scripts/setup_telegram_webhook.py --url https://dentaflow.ai/api/v1/telegram/webhook
```

### 4. Test
```
1. Open Telegram
2. Search: @dentaflow_bot
3. Send: /start
4. Bot responds: "שלום! אני עוזר..."
```

## ✅ Done!

Bot is now live and ready to receive messages.

## 📚 Full Documentation

See `docs/TELEGRAM_BOT_SETUP.md` for:
- Detailed setup instructions
- Conversation examples
- Security configuration
- Monitoring and troubleshooting
- Testing guide

## 🔧 Commands

```bash
# Get webhook info
python3 scripts/setup_telegram_webhook.py --info

# Delete webhook
python3 scripts/setup_telegram_webhook.py --delete

# Set webhook
python3 scripts/setup_telegram_webhook.py --url https://your-domain.com/webhook
```

## 🐛 Troubleshooting

**Bot doesn't respond:**
```bash
# Check webhook status
python3 scripts/setup_telegram_webhook.py --info

# Reset webhook
python3 scripts/setup_telegram_webhook.py --url https://dentaflow.ai/api/v1/telegram/webhook
```

**Token invalid:**
```
1. Message @BotFather
2. Send: /token
3. Select your bot
4. Copy new token
5. Update .env file
```

## 📞 Support

- Full docs: `docs/TELEGRAM_BOT_SETUP.md`
- Telegram API: https://core.telegram.org/bots/api
- BotFather: https://t.me/BotFather
