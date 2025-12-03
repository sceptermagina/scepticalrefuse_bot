import logging
import os
from telegram import Update, LabeledPrice, Invoice
from telegram.ext import Application, CommandHandler, ContextTypes, PreCheckoutQueryHandler, MessageHandler, filters

# Configuración de logs (para ver errores en Railway)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- CONFIGURACIÓN ---
# El token se tomará de las Variables de Entorno de Railway
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía un mensaje cuando el comando /start es emitido."""
    await update.message.reply_text(
        "¡Hola! Soy @rubyjuma_bot. Usa /stars para probar un pago con Telegram Stars."
    )

async def send_stars_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía una factura para pagar con Stars."""
    chat_id = update.message.chat_id
    title = "Donación de Prueba"
    description = "Esta es una prueba de pago con 1 Star"
    payload = "Custom-Payload" # Identificador interno para tu referencia
    currency = "XTR" # XTR es el código para Telegram Stars
    price = 1 # Cantidad de Stars
    prices = [LabeledPrice("Donación", price)]

    # Nota: Para Stars, el provider_token se deja vacío si son bienes digitales
    await context.bot.send_invoice(
        chat_id, title, description, payload, "", currency, prices
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde a la consulta de pre-checkout (Obligatorio para pagos)."""
    query = update.pre_checkout_query
    # Si todo está bien, respondemos con ok=True
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirma que el pago fue exitoso."""
    await update.message.reply_text("¡Gracias! He recibido tus Stars correctamente. 🌟")

def main():
    """Inicia el bot."""
    # Verificamos que exista el token
    if not TOKEN:
        print("Error: No se encontró la variable TELEGRAM_BOT_TOKEN")
        return

    application = Application.builder().token(TOKEN).build()

    # Comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stars", send_stars_invoice))

    # Manejadores de pagos
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Iniciar el bot
    application.run_polling()

if __name__ == '__main__':
    main()