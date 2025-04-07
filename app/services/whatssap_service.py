import os
import logging
from twilio.rest import Client

def enviar_whatsapp(numero_destino, mensaje):
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    numero_origen = os.getenv('TWILIO_WHATSAPP_NUMBER')

    if not all([account_sid, auth_token, numero_origen]):
        logging.error("Faltan credenciales de Twilio.")
        return False

    client = Client(account_sid, auth_token)

    try:
        mensaje_enviado = client.messages.create(
            body=mensaje,
            from_=numero_origen,
            to=f'whatsapp:{numero_destino}'
        )
        logging.info(f"Mensaje enviado: {mensaje_enviado.sid}")
        return True
    except Exception as e:
        logging.error(f"Error al enviar mensaje WhatsApp: {e}")
        return False
