import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# --- НАСТРОЙКИ (ВСТАВЬТЕ ВАШИ КЛЮЧИ СЮДА) ---
TELEGRAM_TOKEN = "8641676059:AAGo1KYLD9S7ncljMVvU0QtwhY8q7xjevlQ"
DEEPSEEK_API_KEY = "sk-cb7c8f4624694e90906a0eec4e029403"
# -------------------------------------------

# Настройка клиента DeepSeek (он совместим с OpenAI библиотекой)
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# Включаем логирование, чтобы видеть ошибки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - приветствие"""
    await update.message.reply_text("Привет! Я DeepSeek. Добавь меня в группу и пиши @моё_имя, чтобы спросить совет.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений, где упомянули бота"""
    # Проверяем, упомянули ли бота в группе
    if update.message.chat.type != "private" and not update.message.mention:
        return # В группе, но без упоминания — игнорируем
        
    # Показываем статус "печатает" в Telegram
    await update.message.chat.send_action(action="typing")
    
    user_message = update.message.text
    
    # Убираем @имя_бота из сообщения (если есть)
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == "mention":
                mention_text = user_message[entity.offset:entity.offset+entity.length]
                if mention_text == f"@{context.bot.username}":
                    user_message = user_message.replace(mention_text, "").strip()
                    break

    try:
        # Запрос к DeepSeek API
        response = client.chat.completions.create(
            model="deepseek-chat", # Используем самую быструю модель[citation:2]
            messages=[
                {"role": "system", "content": "Ты — полезный и дружелюбный собеседник в чате. Отвечай кратко и по делу. Используй русский язык."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=600,
            temperature=0.7
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await update.message.reply_text("Ошибка. Попробуй позже.")

def main():
    """Запуск бота"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()