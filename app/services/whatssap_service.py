from twilio.rest import Client


def enviar_whatsapp(numero, mensaje):
    account_sid = 'tu_account_sid'
    auth_token = 'tu_auth_token'
    client = Client(account_sid, auth_token)

    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=mensaje,
            to=f'whatsapp:{numero}'
        )
        print(f"Mensaje enviado a {numero}: {message.sid}")
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")
