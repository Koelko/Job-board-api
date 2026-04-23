from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import os
load_dotenv()
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)
inspector = inspect(engine)
columns = inspector.get_columns('applications')
print("Структура таблицы: \n")
print(f"{'Поле':<25} {'Тип':<15} {'NULL':<6} {'Default':<20}")
print("-" * 70)
for c in columns:
    name = c['name']
    type_ = str(c['type'])
    nullable = "YES" if c['nullable'] else "NO"
    default = c['default'] if c['default'] is not None else "None"
    print(f"{name:<25} {type_:<15} {nullable:<6} {default:<20}")