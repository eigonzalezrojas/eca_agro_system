import bcrypt

password = "UT.17116"
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed_password.decode('utf-8'))