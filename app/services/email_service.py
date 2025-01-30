import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo_bienvenida(destinatario, nombre, apellido, rut, password_provisoria):
    # Obtener configuración desde las variables de entorno
    remitente = os.getenv('EMAIL_USER')
    contraseña = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    # Configurar el asunto y el mensaje
    asunto = "Bienvenido al sistema de ECA Innovation"
    mensaje = f"""
    Hola {nombre} {apellido},

    Bienvenido al sistema de ECA Innovation. Tu cuenta ha sido creada exitosamente.

    Tus credenciales de acceso son:
    - Usuario: {rut}
    - Contraseña provisoria: {password_provisoria}

    Por favor, inicia sesión en el sistema y cambia tu contraseña en la opción "Perfil" para mayor seguridad.

    Si tienes alguna duda o consulta, no dudes en escribirnos a: ecainnovation@gmail.com.

    Saludos cordiales,
    Equipo de ECA Innovation
    """

    # Configurar el mensaje de correo
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
        return True
    except smtplib.SMTPException as e:
        print(f"Error al enviar el correo: {e}")
        return False