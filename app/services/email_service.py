import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo(destinatario, asunto, mensaje):
    remitente = os.getenv('EMAIL_USER')
    contraseña = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    # Configurar el mensaje
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        # Conectar al servidor SMTP
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, contraseña)
        servidor.send_message(msg)
        servidor.quit()
        print(f"Correo enviado a {destinatario}")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")