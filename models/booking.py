"""Данные бронирования для системы бронирования ресторана (без логики БД)."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class BookingStatus(str, Enum):
    """Статус бронирования."""
    PENDING = "pending"      # Ожидает подтверждения
    CONFIRMED = "confirmed"  # Подтверждено
    CANCELLED = "cancelled"  # Отменено
    COMPLETED = "completed"  # Завершено (гости поели и ушли)

@dataclass
class Booking:
    """
    Какие поля будут у бронирования в приложении и в хранилище.
    Связывает пользователя и стол через систему бронирования.
    """
    # СНАЧАЛА поля БЕЗ значений по умолчанию:
    
    # user_id - внешний ключ на пользователя (кто делает бронь)
    user_id: int
    
    # table_id - внешний ключ на стол (какой стол бронируется)
    table_id: int
    
    # booking_date - дата бронирования
    booking_date: datetime
    
    # start_time - время начала бронирования
    start_time: datetime
    
    # end_time - время окончания бронирования
    end_time: datetime
    
    # guest_count - количество гостей
    guest_count: int
    
    # ПОТОМ поля СО значениями по умолчанию:
    
    # booking_id - первичный ключ
    booking_id: int | None = None
    
    # status - текущий статус бронирования
    status: BookingStatus = BookingStatus.PENDING
    
    # created_at, updated_at - временные метки
    created_at: datetime | None = None
    updated_at: datetime | None = None

__all__ = ["Booking", "BookingStatus"]