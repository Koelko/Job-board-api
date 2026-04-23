import secrets

# Генерируем случайную строку (32 байта = 256 бит)
key = secrets.token_urlsafe(32)
print(key)