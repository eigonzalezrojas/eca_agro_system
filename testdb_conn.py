from sqlalchemy import text  # Importa text desde SQLAlchemy
from app import create_app, db
from app.models import NodeTH

app = create_app()

with app.app_context():
    try:
        # Probar la conexión básica usando text()
        db.session.execute(text('SELECT 1'))
        print("Conexión básica exitosa")

        # Probar la consulta a la tabla nodeTH
        results = NodeTH.query.all()
        print("\nRegistros en la tabla nodeTH:")
        for row in results:
            print(f"ID: {row.id}, ChipID: {row.chipid}, "
                  f"Fecha: {row.fecha}, "
                  f"Temperatura: {row.temperatura}, "
                  f"Humedad: {row.humedad}")

    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")