#!/usr/bin/env python3
"""
Setup Telegram Webhook

This script configures the Telegram webhook to point to your backend server.
Run this after deploying your backend to make the bot live.

Usage:
    python scripts/setup_telegram_webhook.py --url https://your-domain.com/api/v1/telegram/webhook
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.telegram_client import telegram_client


async def setup_webhook(webhook_url: str):
    """
    Set up Telegram webhook.
    
    Args:
        webhook_url: HTTPS URL for webhook
    """
    print(f"🔧 Setting up Telegram webhook...")
    print(f"📍 Webhook URL: {webhook_url}")
    
    try:
        # Set webhook
        result = await telegram_client.set_webhook(webhook_url)
        
        if result.get("ok"):
            print("✅ Webhook set successfully!")
            print(f"📊 Result: {result}")
        else:
            print(f"❌ Failed to set webhook: {result}")
            return False
        
        # Verify webhook
        print("\n🔍 Verifying webhook...")
        info = await telegram_client.get_webhook_info()
        
        if info.get("ok"):
            webhook_info = info.get("result", {})
            print(f"✅ Webhook verified!")
            print(f"📍 URL: {webhook_info.get('url')}")
            print(f"📊 Pending updates: {webhook_info.get('pending_update_count', 0)}")
            
            if webhook_info.get('last_error_message'):
                print(f"⚠️  Last error: {webhook_info.get('last_error_message')}")
                print(f"    Error date: {webhook_info.get('last_error_date')}")
        else:
            print(f"❌ Failed to verify webhook: {info}")
            return False
        
        print("\n🎉 Telegram bot is now live!")
        print(f"💬 Users can start chatting at: https://t.me/dental_clinic_ai_bot")
        
        return True
    
    except Exception as e:
        print(f"❌ Error setting up webhook: {e}")
        return False
    finally:
        await telegram_client.close()


async def delete_webhook():
    """Delete the current webhook."""
    print("🗑️  Deleting webhook...")
    
    try:
        result = await telegram_client.delete_webhook()
        
        if result.get("ok"):
            print("✅ Webhook deleted successfully!")
        else:
            print(f"❌ Failed to delete webhook: {result}")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error deleting webhook: {e}")
        return False
    finally:
        await telegram_client.close()


async def get_webhook_info():
    """Get current webhook information."""
    print("🔍 Getting webhook info...")
    
    try:
        info = await telegram_client.get_webhook_info()
        
        if info.get("ok"):
            webhook_info = info.get("result", {})
            print("\n📊 Webhook Information:")
            print(f"   URL: {webhook_info.get('url') or '(not set)'}")
            print(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
            print(f"   Max connections: {webhook_info.get('max_connections', 40)}")
            
            if webhook_info.get('last_error_message'):
                print(f"\n⚠️  Last Error:")
                print(f"   Message: {webhook_info.get('last_error_message')}")
                print(f"   Date: {webhook_info.get('last_error_date')}")
            else:
                print("\n✅ No errors")
        else:
            print(f"❌ Failed to get webhook info: {info}")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error getting webhook info: {e}")
        return False
    finally:
        await telegram_client.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Setup Telegram webhook for Dental Clinic AI bot"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="Webhook URL (HTTPS required)",
    )
    
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the current webhook",
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Get current webhook information",
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.delete:
        success = asyncio.run(delete_webhook())
    elif args.info:
        success = asyncio.run(get_webhook_info())
    elif args.url:
        # Validate HTTPS
        if not args.url.startswith("https://"):
            print("❌ Error: Webhook URL must use HTTPS")
            sys.exit(1)
        
        success = asyncio.run(setup_webhook(args.url))
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print("   # Set webhook")
        print("   python scripts/setup_telegram_webhook.py --url https://api.example.com/api/v1/telegram/webhook")
        print("\n   # Get webhook info")
        print("   python scripts/setup_telegram_webhook.py --info")
        print("\n   # Delete webhook")
        print("   python scripts/setup_telegram_webhook.py --delete")
        sys.exit(0)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
