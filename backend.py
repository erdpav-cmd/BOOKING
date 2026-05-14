"""
Файл для инициализации базы данных и CRUD операций.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from postgres_driver import PostgresDriver
from models.user import User
from models.tables import Table
from models.booking import Booking

def get_db():
    """Вспомогательная функция для получения подключения к БД."""
    return PostgresDriver()

def create_tables():
    """Создает таблицы в базе данных на основе моделей."""
    print("Подключение к базе данных и создание таблиц...")
    with get_db() as db:
        db.create_table_from_model(User)
        db.create_table_from_model(Table)
        db.create_table_from_model(Booking)
    print("✅ Инициализация завершена!")

def create_user(email: str, password_hash: str, first_name: str, last_name: str, 
                phone: str = None, role: str = "user", status: str = "active"):
    with get_db() as db:
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "role": role,
            "status": status
        }
        return db.create("users", user_data, returning="*")

def get_all_users():
    with get_db() as db:
        return db.read("users", order_by="user_id DESC")

def create_table(table_number: str, capacity: int, location: str, status: str = "available",
                 description: str = None, hourly_rate: float = None, 
                 has_window_view: bool = False, is_smoking_allowed: bool = False):
    with get_db() as db:
        table_data = {
            "table_number": table_number,
            "capacity": capacity,
            "location": location,
            "status": status,
            "description": description,
            "hourly_rate": hourly_rate,
            "has_window_view": has_window_view,
            "is_smoking_allowed": is_smoking_allowed
        }
        return db.create("tables", table_data, returning="*")

def get_all_tables():
    with get_db() as db:
        return db.read("tables", order_by="table_id DESC")

def create_booking(user_id: int, table_id: int, booking_date: str, start_time: str, end_time: str, guest_count: int):
    with get_db() as db:
        booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%d")
        start_time_obj = datetime.strptime(start_time, "%H:%M")
        end_time_obj = datetime.strptime(end_time, "%H:%M")
        
        full_start = booking_date_obj.replace(hour=start_time_obj.hour, minute=start_time_obj.minute)
        full_end = booking_date_obj.replace(hour=end_time_obj.hour, minute=end_time_obj.minute)

        if not check_table_availability(table_id, full_start, full_end, db=db):
            return False

        booking_data = {
            "user_id": user_id,
            "table_id": table_id,
            "booking_date": full_start,
            "start_time": full_start,
            "end_time": full_end,
            "guest_count": guest_count
        }
        return db.create("bookings", booking_data, returning="*")

def get_all_bookings():
    with get_db() as db:
        return db.read("bookings", order_by="booking_id DESC")

def check_table_availability(
    table_id: int,
    start_time: datetime,
    end_time: datetime,
    db: Optional[PostgresDriver] = None,
) -> bool:
    """True, если стол свободен в интервале [start_time, end_time]."""
    # Колонки start_time/end_time в старых БД могли быть TEXT — сравниваем как timestamp
    query = """
        SELECT COUNT(*) AS count FROM bookings
        WHERE table_id = %s
        AND start_time::timestamp < %s
        AND end_time::timestamp > %s
    """

    def _run(driver: PostgresDriver) -> bool:
        driver.cursor.execute(query, (table_id, end_time, start_time))
        result = driver.cursor.fetchone()
        count = result["count"] if result else 0
        return count == 0

    if db is not None:
        return _run(db)
    with get_db() as conn:
        return _run(conn)

if __name__ == "__main__":
    create_tables()