import logging, requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = "8455111408:AAFG0doukDgec2jVBafKvzGOVTxnXLxeXCk"

# Generate temp mail
def generate_email():
    resp = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1")
    return resp.json()[0]

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = generate_email()
    context.user_data["email"] = email
    await update.message.reply_text(
        f"👋 Welcome to Temp Mail Bot!\n\n"
        f"📧 Your Email: {email}\n\n"
        f"Commands:\n"
        f"/inbox - Check inbox\n"
        f"/delete - Delete email\n"
        f"/new - Generate new email\n\n"
        f"⚡ Powered by Shakil"
    )

# /inbox command
async def inbox(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = context.user_data.get("email")
    if not email:
        await update.message.reply_text("❌ No email set. Use /start first.")
        return
    login, domain = email.split("@")
    resp = requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}")
    mails = resp.json()
    if not mails:
        await update.message.reply_text("📭 Inbox is empty.")
    else:
        text = "📨 Inbox:\n\n"
        for m in mails:
            text += f"From: {m['from']}\nSubject: {m['subject']}\n\n"
        await update.message.reply_text(text)

# /delete command
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "email" in context.user_data:
        del context.user_data["email"]
        await update.message.reply_text("🗑️ Email deleted successfully.")
    else:
        await update.message.reply_text("❌ No email to delete.")

# /new command
async def new_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = generate_email()
    context.user_data["email"] = email
    await update.message.reply_text(
        f"🔄 New Temp Mail Generated!\n📧 {email}\n\n"
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
