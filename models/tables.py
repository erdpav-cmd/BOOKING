"""Данные стола для системы бронирования."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TableStatus(str, Enum):
    """Статус стола."""
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    CLEANING = "cleaning"
    BROKEN = "broken"

class TableLocation(str, Enum):
    """Расположение стола."""
    MAIN_HALL = "main_hall"
    TERRACE = "terrace"
    VIP_ROOM = "vip_room"

@dataclass
class Table:
    """Модель стола."""
    # Обязательные поля
    table_number: str
    capacity: int
    location: TableLocation
    
    # Необязательные
    table_id: int | None = None
    status: TableStatus = TableStatus.AVAILABLE
    description: str | None = None
    hourly_rate: float | None = None
    has_window_view: bool = False  # Вид из окна
    is_smoking_allowed: bool = False  # Курение разрешено
    created_at: datetime | None = None
    updated_at: datetime | None = None

__all__ = ["Table", "TableStatus", "TableLocation"]