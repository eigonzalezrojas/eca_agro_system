import random
import string
import bcrypt

def generar_password_hash(longitud=8):
    caracteres = string.ascii_letters + string.digits
    password = ''.join(random.choice(caracteres) for _ in range(longitud))
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    return password, hashed_password.decode('utf-8')