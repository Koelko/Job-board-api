from security import create_access_token, verify_token

token = create_access_token({"user_id": 1, "user_type": "employer"})
print(f"Токен создан: {token[:50]}...")  
result = verify_token(token)
print(f"Проверка: {result}")
print(f"Тип результата: {type(result)}") 