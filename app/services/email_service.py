import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def enviar_correo_bienvenida(destinatario, nombre, apellido, rut, password_provisoria):
    # Obtener configuración desde las variables de entorno
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
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

    Por favor, inicia sesión en el sistema mediante la url

    https://ecainnovation.cl/sistema/

    Cambia tu contraseña en la opción "Perfil" para mayor seguridad.

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
        servidor.login(remitente, password)
        servidor.send_message(msg)
        servidor.quit()
        print(f"Correo enviado a {destinatario}")
        return True
    except smtplib.SMTPException as e:
        print(f"Error al enviar el correo: {e}")
        return False


def enviar_correo_alerta(destinatario, titulo, descripcion, instruccion):
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    asunto = f"⚠️ Alerta Climática: {titulo}"
    mensaje = f"""
    Se ha detectado una alerta climática en tu zona:

    🔴 Evento: {titulo}
    📌 Descripción: {descripcion}
    🛑 Instrucciones: {instruccion}

    Por favor, toma las precauciones necesarias.

    Saludos,
    Equipo de ECA Innovation
    """

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.send_message(msg)
        servidor.quit()
        print(f"📩 Alerta enviada a {destinatario}")
        return True
    except smtplib.SMTPException as e:
        print(f"Error al enviar la alerta: {e}")
        return False


def alerta_temperatura_eca(destinatario, cultivo, fase, temperatura, mensaje_alerta):
    """
    Envía una alerta de temperatura al cliente asociado a un cultivo y fase.
    """
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    asunto = f"🌡️ Alerta de Temperatura - {cultivo} ({fase})"
    mensaje = f"""
    ⚠️ Se ha detectado una anomalía en la temperatura para el cultivo {cultivo} en la fase {fase}.

    📌 Temperatura actual: {temperatura}°C
    🚨 {mensaje_alerta}

    Por favor, revisa las condiciones del cultivo y toma medidas si es necesario.

    Saludos,
    Equipo de ECA Innovation
    """

    # Solo se envía al cliente, NO al administrador
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        print(f"📩 Alerta de temperatura enviada a {destinatario}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar la alerta de temperatura al cliente: {e}")
        return False


def alerta_temperatura_admin(chipid, temperatura, mensaje_alerta):
    """
    Envía una única alerta de temperatura al administrador por dispositivo (chipid).
    """
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))
    email_admin = os.getenv('EMAIL_ADMIN')

    if not email_admin:
        print("❌ ERROR: No se ha definido el EMAIL_ADMIN en el archivo .env")
        return False

    asunto = f"🌡️ Alerta de Temperatura - Dispositivo {chipid}"
    mensaje = f"""
    🚨 Se ha detectado una anomalía de temperatura en el dispositivo {chipid}.

    📌 Temperatura actual: {temperatura}°C
    🛑 {mensaje_alerta}

    🔍 Se recomienda revisar las condiciones del equipo y la zona de monitoreo.

    Saludos,
    Equipo de ECA Innovation
    """

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = email_admin
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, email_admin, msg.as_string())
        servidor.quit()
        print(f"📩 Alerta de temperatura enviada a {email_admin} para el dispositivo {chipid}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar la alerta de temperatura al administrador: {e}")
        return False


def alerta_humedad_cliente(destinatario, cultivo, fase, humedad_min, humedad_max, mensaje_alerta):
    """
    Envía una alerta de humedad al cliente asociado a un cultivo y fase.
    """
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    asunto = f"💧 Alerta de Humedad - {cultivo} ({fase})"
    mensaje = f"""
    ⚠️ Se ha detectado una anomalía en la humedad para el cultivo {cultivo} en la fase {fase}.

    📌 Humedades registradas: Min {humedad_min}% / Max {humedad_max}%
    🚨 {mensaje_alerta}

    Por favor, revisa las condiciones del cultivo y toma medidas si es necesario.

    Saludos,
    Equipo de ECA Innovation
    """

    # Enviar solo al cliente
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        print(f"📩 Alerta de humedad enviada a {destinatario}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar la alerta de humedad al cliente: {e}")
        return False


def enviar_correo_cambio_fase(destinatario=None, asunto=None, mensaje=None, cc_destinatario=None):
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto

    # Agregar copia si se proporciona un destinatario en CC
    if cc_destinatario:
        msg['Cc'] = cc_destinatario
        destinatarios = [destinatario, cc_destinatario]
    else:
        destinatarios = [destinatario]

    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatarios, msg.as_string())
        servidor.quit()
        print(
            f"📩 Notificación de cambio de fase enviada a {destinatario} con copia a {cc_destinatario if cc_destinatario else 'N/A'}")
        return True
    except smtplib.SMTPException as e:
        print(f"Error al enviar la notificación de cambio de fase: {e}")
        return False


def enviar_alerta_data(chipid, parcela, cliente, cultivo, ultima_fecha):
    """
    Envía una alerta cuando un dispositivo deja de enviar datos.
    """

    # Obtener configuración del correo desde variables de entorno
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    # Destinatarios
    destinatario_principal = "correo1@gmail.com"
    destinatario_cc = "correo2@gmail.com"

    # Asunto del correo
    asunto = f"⚠️ Alerta de Dispositivo {chipid} sin datos recientes"

    # Mensaje del correo
    mensaje = f"""
    Estimado equipo de ECA Innovation,

    🚨 Se ha detectado que el dispositivo con chip ID {chipid} ha dejado de enviar datos.

    📌 Información relevante:
    - 📍 Parcela: {parcela}
    - 👤 Cliente: {cliente}
    - 🌱 Cultivo: {cultivo}
    - ⏳ Última transmisión registrada: {ultima_fecha.strftime("%Y-%m-%d %H:%M:%S")}

    🛑 Se recomienda realizar una inspección en terreno para verificar posibles causas:
    - Verificar batería del dispositivo
    - Revisar la conexión a la red
    - Evaluar posibles problemas ambientales que afecten la señal

    🚀 Acción sugerida: Coordinar visita de revisión técnica para diagnóstico.

    Saludos,
    Equipo de ECA Innovation
    """

    # Configurar el mensaje de correo
    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario_principal
    msg['Cc'] = destinatario_cc
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    # Lista de destinatarios
    destinatarios = [destinatario_principal, destinatario_cc]

    try:
        # Conectar al servidor SMTP
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatarios, msg.as_string())
        servidor.quit()

        print(f"📩 Alerta de dispositivo sin datos enviada a {', '.join(destinatarios)}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar la alerta de dispositivo sin datos: {e}")
        return False


def enviar_alerta_cliente(destinatario, chipid, parcela, cultivo, ultima_fecha):
    """
    Envía una alerta a un cliente cuando un dispositivo deja de enviar datos.
    """
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    asunto = f"⚠️ Alerta: Dispositivo {chipid} sin datos recientes"
    mensaje = f"""
    Estimado usuario,

    🚨 El dispositivo con Chip ID **{chipid}** ha dejado de enviar datos.

    📌 Información:
    - 📍 Parcela: {parcela}
    - 🌱 Cultivo: {cultivo}
    - ⏳ Última transmisión registrada: {ultima_fecha.strftime("%Y-%m-%d %H:%M:%S")}

    🛑 Se recomienda verificar:
    - Batería del dispositivo
    - Conexión de red
    - Posibles interferencias

    Saludos,
    Equipo de ECA Innovation
    """

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        print(f"📩 Alerta enviada a {destinatario} sobre el dispositivo {chipid}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar la alerta al cliente: {e}")
        return False


def enviar_alerta_dispositivo_admin(chipid, ultima_fecha):
    """
    Envía una única alerta de dispositivo al administrador cuando un dispositivo deja de enviar datos.
    """
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))
    email_admin = os.getenv('EMAIL_ADMIN')  # Obtener correo del administrador

    if not email_admin:
        print("❌ ERROR: No se ha definido EMAIL_ADMIN en el archivo .env")
        return False

    asunto = f"🚨 Alerta: Dispositivo {chipid} sin datos recientes"
    mensaje = f"""
    Estimado equipo de ECA Innovation,

    🚨 El dispositivo con Chip ID **{chipid}** ha dejado de enviar datos.

    📌 Última transmisión registrada: {ultima_fecha.strftime("%Y-%m-%d %H:%M:%S")}

    🛑 Se recomienda realizar una inspección en terreno para verificar:
    - Batería del dispositivo
    - Conexión a la red
    - Posibles problemas ambientales que afecten la señal

    Saludos,
    Equipo de ECA Innovation
    """

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = email_admin
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, email_admin, msg.as_string())
        servidor.quit()
        print(f"📩 Alerta enviada a {email_admin} sobre el dispositivo {chipid}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar la alerta al administrador: {e}")
        return False


def enviar_recuperar_clave(destinatario, asunto, mensaje):
    """Envía un correo utilizando SMTP y variables de entorno."""
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        print(f"✅ Correo enviado a {destinatario}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar el correo: {e}")
        return False


def enviar_reporte_diario(destinatario, cultivo, fase, reporte):
    """
    Envía un reporte diario al cliente asociado a un cultivo y fase,
    incluyendo el porcentaje de tiempo en condiciones óptimas, sobre temperatura máxima,
    bajo temperatura mínima, sobre humedad máxima y bajo humedad mínima.
    """
    remitente = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    host = os.getenv('EMAIL_HOST')
    port = int(os.getenv('EMAIL_PORT'))

    asunto = f"📊 Reporte Diario - {cultivo} ({fase})"
    mensaje = f"""
    🌱 Resumen del día para el cultivo {cultivo} en la fase {fase}:

    📆 Fecha: {reporte['Fecha']}
    🌡️ Temperatura Máxima: {reporte['Temperatura Máxima']}°C
    ❄️ Temperatura Mínima: {reporte['Temperatura Mínima']}°C
    💧 Óptimo del cultivo durante el día: {reporte['Porcentaje Óptimo']}%
    🔥 Porcentaje sobre temperatura máxima: {reporte['Porcentaje Sobre Máxima']}%
    ❄️ Porcentaje bajo temperatura mínima: {reporte['Porcentaje Bajo Mínima']}%
    💦 Porcentaje sobre humedad máxima: {reporte['Porcentaje Sobre Humedad Máxima']}%
    💧 Porcentaje bajo humedad mínima: {reporte['Porcentaje Bajo Humedad Mínima']}%
    ⏳ Horas Frío: {reporte['Horas Frío']}
    📈 GDA: {reporte['GDA']}

    Saludos,
    Equipo de ECA Innovation
    """

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(mensaje, 'plain'))

    try:
        servidor = smtplib.SMTP(host, port)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.sendmail(remitente, destinatario, msg.as_string())
        servidor.quit()
        print(f"📩 Reporte diario enviado a {destinatario}")
        return True
    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar el reporte diario al cliente: {e}")
        return False