import logging
import os
from telegram import Update, LabeledPrice, Invoice
from telegram.ext import Application, CommandHandler, ContextTypes, PreCheckoutQueryHandler, MessageHandler, filters

# Configuración de logs básica
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Tomar token de Railway
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde al comando /start"""
    await update.message.reply_text(
        "¡Hola! Soy @scepticalrefuse_bot. Estoy vivo en Railway.\nUsa /stars para probar el pago."
    )

async def send_stars_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía la factura de Stars corregida"""
    chat_id = update.message.chat_id
    
    # DATOS DE LA FACTURA
    title = "Donación de Prueba"
    description = "Prueba de 1 Star"
    payload = "Custom-Payload"
    currency = "XTR"  # Moneda de Stars
    price = 1  # Cantidad
    prices = [LabeledPrice("Donación", price)]

    # ENVÍO DE FACTURA (Forma corregida para v21+)
    # Usamos argumentos con nombre (chat_id=..., title=...) para evitar errores
    try:
        await context.bot.send_invoice(
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token="", # DEBE estar vacío para Stars, pero debe enviarse
            currency=currency,
            prices=prices
        )
    except Exception as e:
        # Si falla, el bot te lo dirá en el chat
        await update.message.reply_text(f"Error enviando factura: {e}")
        print(f"ERROR ENVIANDO FACTURA: {e}")

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Acepta el pago antes de procesarlo"""
    query = update.pre_checkout_query
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirma el pago exitoso"""
    await update.message.reply_text("¡Pago recibido! Gracias por tus Stars 🌟")

def main():
    if not TOKEN:
        print("ERROR: Falta el Token en las variables de entorno.")
        return

    # Construimos la aplicación
    application = Application.builder().token(TOKEN).build()

    # Añadimos los manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stars", send_stars_invoice))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Iniciamos el bot
    print("Bot iniciando...")
    application.run_polling()

if __name__ == '__main__':
    main()
