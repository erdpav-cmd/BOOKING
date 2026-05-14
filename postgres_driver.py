import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Tuple, Any
import os
from dotenv import load_dotenv
from typing import get_origin, get_args, Union
from datetime import datetime

load_dotenv()

class PostgresDriver:
    """Драйвер для подключения к PostgreSQL."""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.database = os.getenv("DB_NAME", "booking")
        self.user = os.getenv("DB_USER", "admin")
        self.password = os.getenv("DB_PASSWORD", "admin")
        self.port = os.getenv("DB_PORT", "5432")
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Устанавливает подключение к базе данных."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print(f"✅ Подключение к БД '{self.database}' установлено")
            return True
        except OperationalError as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return False

    def disconnect(self):
        """Закрывает подключение к базе данных."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("🔌 Подключение к БД закрыто")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> bool:
        """Выполняет SQL запрос."""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"❌ Ошибка выполнения запроса: {e}")
            self.connection.rollback()
            return False

    def _check_table_exists(self, table_name: str) -> bool:
        """Проверяет, существует ли таблица."""
        query = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """
        try:
            self.cursor.execute(query, (table_name,))
            row = self.cursor.fetchone()
            if row is None:
                return False
            # RealDictCursor: строка — словарь по имени колонки
            return bool(next(iter(row.values())))
        except Exception:
            return False

    def create_table_from_model(self, model_class):
        """Создает таблицу в БД на основе Dataclass модели."""
        table_name = model_class.__name__.lower() + "s"
        
        if not self._check_table_exists(table_name):
            sql = self._generate_create_table_sql(model_class, table_name)
            self.execute_query(sql)
            print(f"✅ Таблица '{table_name}' создана.")
        else:
            print(f"⚠️ Таблица '{table_name}' уже существует.")

    def _generate_create_table_sql(self, model_class, table_name):
        """Генерирует SQL запрос CREATE TABLE на основе аннотаций типов модели."""
        fields = []
        annotations = model_class.__annotations__
        
        # Определяем имя поля первичного ключа
        pk_field = f"{table_name[:-1]}_id"

        for field_name, field_type in annotations.items():
            origin = get_origin(field_type)
            if origin is Union:
                args = get_args(field_type)
                actual_type = next((arg for arg in args if arg is not type(None)), str)
            else:
                actual_type = field_type

            sql_type = self._python_type_to_postgres(actual_type)
            
            if field_name == pk_field:
                fields.append(f"{field_name} SERIAL PRIMARY KEY")
            elif field_name.endswith("_id"):
                fields.append(f"{field_name} INTEGER")
            else:
                fields.append(f"{field_name} {sql_type}")

        columns_sql = ", ".join(fields)
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});"

    def _python_type_to_postgres(self, py_type):
        """Сопоставляет типы Python с типами Postgres."""
        mapping = {
            int: "INTEGER",
            str: "VARCHAR(255)",
            bool: "BOOLEAN",
            float: "FLOAT",
            datetime: "TIMESTAMP",  # ИСПРАВЛЕНИЕ: добавлена обработка datetime
        }
        
        if isinstance(py_type, type) and issubclass(py_type, str):
            return "VARCHAR(255)"
            
        return mapping.get(py_type, "TEXT")

    def read(self, table: str, columns: str = "*", where: str = None, 
             params: tuple = None, order_by: str = None, limit: int = None, 
             offset: int = None) -> List[dict]:
        """SELECT запрос."""
        query = f"SELECT {columns} FROM {table}"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"❌ Ошибка чтения данных: {e}")
            return []

    def create(self, table: str, row: dict, returning: str = None):
        """INSERT одной строки."""
        columns = ", ".join(row.keys())
        placeholders = ", ".join(["%s"] * len(row))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        if returning:
            query += f" RETURNING {returning}"
        
        try:
            self.cursor.execute(query, list(row.values()))
            self.connection.commit()
            
            if returning:
                return self.cursor.fetchone()
            return self.cursor.rowcount
        except Exception as e:
            print(f"❌ Ошибка создания записи: {e}")
            self.connection.rollback()
            return None

    def update(self, table: str, data: dict, where: str, where_params: tuple = None, returning: str = None):
        """UPDATE записи."""
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where}"
        
        if returning:
            query += f" RETURNING {returning}"
        
        params = list(data.values())
        if where_params:
            params.extend(where_params)
        
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            
            if returning:
                return self.cursor.fetchall()
            return self.cursor.rowcount
        except Exception as e:
            print(f"❌ Ошибка обновления: {e}")
            self.connection.rollback()
            return None

    def delete(self, table: str, where: str, where_params: tuple = None, returning: str = None):
        """DELETE записи."""
        query = f"DELETE FROM {table} WHERE {where}"
        
        if returning:
            query += f" RETURNING {returning}"
        
        try:
            if where_params:
                self.cursor.execute(query, where_params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            
            if returning:
                return self.cursor.fetchall()
            return self.cursor.rowcount
        except Exception as e:
            print(f"❌ Ошибка удаления: {e}")
            self.connection.rollback()
            return None

    def __enter__(self):
        """Контекстный менеджер: вход."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Контекстный менеджер: выход."""
        if self.connection is not None:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
        self.disconnect()