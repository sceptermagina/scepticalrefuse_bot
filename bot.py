import logging
import os
from telegram import Update, LabeledPrice
from telegram.ext import Application, CommandHandler, ContextTypes, PreCheckoutQueryHandler, MessageHandler, filters

# Configuración de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Instrucciones de uso"""
    await update.message.reply_text(
        "¡Hola! Soy @scepticalrefuse_bot.\n\n"
        "Para hacer una donación, usa el comando /stars seguido de la cantidad.\n"
        "Ejemplo:\n"
        "🔹 /stars 10 (Para donar 10 estrellas)\n"
        "🔹 /stars 100 (Para donar 100 estrellas)\n\n"
        "Si solo escribes /stars, se cobrará 1 estrella por defecto."
    )

async def send_stars_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Genera una factura con la cantidad elegida por el usuario"""
    chat_id = update.message.chat_id
    
    # 1. DEFINIR EL PRECIO
    # Por defecto cobramos 1 si no escriben nada
    amount = 1 
    
    # Verificamos si el usuario escribió un número (context.args)
    if context.args:
        try:
            # Intentamos convertir lo que escribió a un número entero
            input_amount = int(context.args[0])
            
            if input_amount < 1:
                await update.message.reply_text("❌ El mínimo es 1 estrella.")
                return
            
            amount = input_amount
            
        except ValueError:
            await update.message.reply_text("❌ Por favor escribe un número válido. Ejemplo: /stars 10")
            return

    # 2. CREAR LOS DATOS DE LA FACTURA
    title = f"Donación de {amount} Stars"
    description = f"Muchas gracias por apoyar con {amount} estrellas ⭐"
    payload = f"donacion_{amount}_stars" # Referencia interna
    currency = "XTR" 
    prices = [LabeledPrice("Donación", amount)]

    # 3. ENVIAR LA FACTURA
    try:
        await context.bot.send_invoice(
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token="", # Siempre vacío para Stars
            currency=currency,
            prices=prices
        )
    except Exception as e:
        await update.message.reply_text(f"Ocurrió un error: {e}")
        print(f"ERROR: {e}")

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Aprobación previa al pago"""
    query = update.pre_checkout_query
    # Aquí podrías poner lógica extra, como verificar si el usuario no está baneado, etc.
    await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirmación de pago exitoso"""
    # Podemos saber cuánto pagaron
    payment_info = update.message.successful_payment
    total_amount = payment_info.total_amount # Cantidad de Stars
    
    await update.message.reply_text(
        f"¡Wao! 🤩 He recibido tus {total_amount} Stars correctamente.\n"
        "¡Gracias por tu generosidad!"
    )

def main():
    if not TOKEN:
        print("ERROR: Falta el Token")
        return

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stars", send_stars_invoice))
    
    # Manejadores de pago
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    print("Bot iniciando en Railway...")
    application.run_polling()

if __name__ == '__main__':
    main()
