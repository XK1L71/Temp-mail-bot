import logging, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = "8455111408:AAFG0doukDgec2jVBafKvzGOVTxnXLxeXCk"

BASE_URL = "https://api.mail.tm"

# Create account + email
def generate_email():
    try:
        # random username
        import uuid
        username = str(uuid.uuid4())[:8]
        password = "Pass@" + username

        # register temp mail
        resp = requests.post(
            f"{BASE_URL}/accounts",
            json={"address": f"{username}@bugfoo.com", "password": password},
            timeout=8,
        )
        if resp.status_code not in (200, 201):
            return None

        email = resp.json()["address"]

        # login to get token
        token_resp = requests.post(
            f"{BASE_URL}/token",
            json={"address": email, "password": password},
            timeout=8,
        )
        token = token_resp.json().get("token")

        return {"email": email, "password": password, "token": token}
    except Exception as e:
        logging.error(f"Email generate error: {e}")
        return None

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account = generate_email()
    if not account:
        await update.message.reply_text("⚠️ Could not generate email. Try again later.")
        return
    context.user_data["account"] = account
    await update.message.reply_text(
        f"👋 Welcome to Temp Mail Bot!\n\n"
        f"📧 Your Email: {account['email']}\n\n"
        f"Commands:\n"
        f"/inbox - Check inbox\n"
        f"/delete - Delete email\n"
        f"/new - Generate new email\n\n"
        f"⚡ Powered by Shakil"
    )

# /inbox command
async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account = context.user_data.get("account")
    if not account:
        await update.message.reply_text("❌ No email set. Use /start first.")
        return
    try:
        headers = {"Authorization": f"Bearer {account['token']}"}
        resp = requests.get(f"{BASE_URL}/messages", headers=headers, timeout=8)
        mails = resp.json().get("hydra:member", [])

        if not mails:
            await update.message.reply_text("📭 Inbox is empty.")
        else:
            text = "📨 Inbox:\n\n"
            for m in mails:
                text += f"From: {m['from']['address']}\nSubject: {m['subject']}\n\n"
            await update.message.reply_text(text)
    except Exception as e:
        logging.error(f"Inbox error: {e}")
        await update.message.reply_text("⚠️ Failed to load inbox. Try again later.")

# /delete command
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "account" in context.user_data:
        del context.user_data["account"]
        await update.message.reply_text("🗑️ Email deleted successfully.")
    else:
        await update.message.reply_text("❌ No email to delete.")

# /new command
async def new_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account = generate_email()
    if not account:
        await update.message.reply_text("⚠️ Could not generate new email. Try again later.")
        return
    context.user_data["account"] = account
    await update.message.reply_text(
        f"🔄 New Temp Mail Generated!\n📧 {account['email']}\n\n"
        f"Use /inbox to check emails."
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("inbox", inbox))
    app.add_handler(CommandHandler("delete", delete))
    app.add_handler(CommandHandler("new", new_email))
    app.run_polling()

if __name__ == "__main__":
    main()
