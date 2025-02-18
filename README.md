# 🌱 ECA Agro System

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/eigonzalezrojas/eca_agro_system)

ECA Agro System es una plataforma de monitoreo agrícola que permite a los agricultores gestionar cultivos, dispositivos IoT, alertas y condiciones climáticas en tiempo real.

## 🚀 Características

✅ Monitoreo de temperatura y humedad en tiempo real.  
✅ Gestión de cultivos, parcelas y dispositivos.  
✅ Sistema de alertas automáticas basado en datos climáticos.  
✅ Notificaciones por correo cuando un dispositivo deja de enviar datos.  
✅ Visualización de datos con gráficos interactivos.  
✅ Dashboard para clientes y administradores.  

---

## 📦 **Requisitos previos**
Antes de instalar el sistema, asegúrate de tener:

- **Python 3.10+**  
- **MySQL 8+**  
- **Node.js + npm** (para la parte frontend si aplica)  
- **Entorno virtual en Python**  
- **Docker (opcional para despliegue)**  

---

## ⚙️ **Instalación y Configuración**

### 1️⃣ **Clonar el repositorio**
```sh
git clone https://github.com/eigonzalezrojas/eca_agro_system.git
cd eca_agro_system
```

### 2️⃣ **Configurar el entorno virtual y dependencias**
```sh
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3️⃣ **Configurar variables de entorno**
Renombrar el archivo `.env.example` a `.env` y editar los valores según tu configuración.

```sh
cp .env.example .env
```

### 4️⃣ **Configurar la base de datos**
En **MySQL**, crear la base de datos:
```sql
CREATE DATABASE ecainnovationcl_system;
```

Luego, importar las tablas:
```sh
mysql -u root -p ecainnovationcl_system < database/schema.sql
```

### 5️⃣ **Ejecutar el servidor**
```sh
flask run
```
El sistema estará disponible en: **http://127.0.0.1:5000**

---

## 🎯 **Uso del Sistema**

- **Acceso Administrador:**  
  - Usuario: `17116106-1`  
  - Contraseña: `*configurada en la base de datos*`  
- **Acceso Cliente:** Cada usuario tiene su propio acceso.  

Para acceder al panel de administración y clientes, ir a:
🔗 **http://127.0.0.1:5000/login**

---

## 📊 **Módulos principales**
- `app/` → Código principal del backend con Flask.  
- `app/models.py` → Definición de modelos SQLAlchemy.  
- `app/routes/` → Rutas de la API y vistas.  
- `app/services/` → Servicios como envío de correos y alertas.  
- `scripts/` → Scripts de monitoreo de dispositivos.  

---

## 🚨 **Monitoreo de Dispositivos**
Cada 1 hora se ejecuta un script que revisa si los dispositivos han dejado de enviar datos y envía alertas por correo.

Ejecutar manualmente:
```sh
python3 app/scripts/verificar_data.py
```

---

## 📩 **Notificaciones y Alertas**
El sistema envía alertas de:
- **Temperaturas extremas en cultivos**  
- **Dispositivos inactivos**  
- **Cambio de fases en cultivos**  

Los correos se envían usando SMTP configurado en `.env`.

---

## 🛠 **Tecnologías Utilizadas**
- **Backend:** Flask + SQLAlchemy  
- **Base de Datos:** MySQL  
- **Frontend:** HTML, Tailwind CSS (si aplica)  
- **IoT:** Integración con sensores de temperatura y humedad  
- **Notificaciones:** SMTP (correos) y Twilio (WhatsApp, futuro)  

---

## 🤝 **Contribuciones**
Si deseas contribuir al proyecto, por favor sigue estos pasos:

1. **Fork** el repositorio
2. Crea una **rama**: `git checkout -b feature/nueva-funcionalidad`
3. Realiza **commits**: `git commit -m "Añadida nueva funcionalidad"`
4. **Push** a tu fork: `git push origin feature/nueva-funcionalidad`
5. Abre un **Pull Request**

---

## 📜 **Licencia**
Este proyecto es de uso privado y está bajo derechos de **ECA Innovation**.

---

## 📞 **Contacto**
📧 Correo: `info@ecainnovation.cl`  
🌐 Web: [ECA Innovation](https://ecainnovation.cl)

---

🚀 **Desarrollado con pasión por [Eithel Gonzalez](https://github.com/eigonzalezrojas)** 🚀

