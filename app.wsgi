import sys
import os

# Ruta del directorio de la aplicación
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Activar el entorno virtual
activate_this = os.path.join(current_dir, "venv/bin/activate")
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Cargar la aplicación Flask
from app import create_app
application = create_app()