"""Данные пользователя мини-системы бронирования."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """Роль в системе (admin/manager/user)."""
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

class UserStatus(str, Enum):
    """Статус пользователя."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    PENDING = "pending"

@dataclass
class User:
    """Модель пользователя."""
    # Сначала обязательные поля
    email: str
    password_hash: str
    first_name: str  # Имя
    last_name: str   # Фамилия
    
    # Потом необязательные
    user_id: int | None = None
    phone: str | None = None
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login: datetime | None = None

__all__ = ["User", "UserRole", "UserStatus"]