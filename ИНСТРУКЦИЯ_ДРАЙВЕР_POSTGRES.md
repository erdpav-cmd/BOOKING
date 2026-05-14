# Инструкция: модуль `postgres_driver`

Общая установка проекта, переменные окружения и запуск приложения описаны в **[README.MD](README.MD)**. Здесь — только поведение драйвера и как он встроен в бронирование.

## Роль в проекте

| Компонент | Связь с драйвером |
|-----------|-------------------|
| `backend.py` | Создаёт экземпляр `PostgresDriver` через `get_db()`, вызывает `create_table_from_model` и методы CRUD |
| `models/` | Dataclass-модели; по их аннотациям драйвер строит `CREATE TABLE` |
| `.env` / `.env.example` | Параметры подключения (см. ниже) |

## Зависимости

Как в [README.MD](README.MD), раздел «Установка»:

```bash
pip install -r requirements.txt
```

Пакеты: `psycopg2-binary`, `python-dotenv`. При импорте `postgres_driver` вызывается `load_dotenv()` — переменные подхватываются из файла `.env` в текущем рабочем каталоге (создайте его из `.env.example`).

## Переменные окружения

Используются **только** отдельные ключи (строка `DATABASE_URL` в коде **не** обрабатывается).

| Переменная | Значение по умолчанию в коде |
|------------|------------------------------|
| `DB_HOST` | `localhost` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `booking` |
| `DB_USER` | `admin` |
| `DB_PASSWORD` | `admin` |

Рекомендуется задать реальные значения в `.env` (шаблон — `.env.example` в корне проекта, как в README).

## Подключение и курсор

- **`PostgresDriver()`** — без аргументов; читает настройки из окружения / `.env`.
- **`connect()`** — открывает соединение и курсор с **`RealDictCursor`**: строки выборок — словари по имени колонки.
- **`disconnect()`** — закрывает курсор и соединение.
- **Контекстный менеджер** `with PostgresDriver() as db:` — вызывает `connect()` при входе; при выходе выполняет `commit` или `rollback` (если было исключение) и `disconnect()`, если соединение было установлено.

Инициализация таблиц из моделей и типовые операции по сущностям — в **`backend.py`** (см. README: `python backend.py`).

## Основные методы

- **`execute_query(query, params=None)`** — произвольный SQL с коммитом при успехе.
- **`create_table_from_model(model_class)`** — имя таблицы: `ИмяКласса` в нижнем регистре + `s` (например, `User` → `users`). Первичный ключ: поле вида `{имя_в_единственном_числе}_id` (например, `user_id`) получает `SERIAL PRIMARY KEY`. Поля с суффиксом `_id` (кроме PK) — `INTEGER`. Остальные типы маппятся из аннотаций (в т.ч. `datetime` → `TIMESTAMP`, str-Enum → `VARCHAR(255)`).
- **`read(table, columns="*", where=None, params=None, order_by=None, limit=None, offset=None)`** — `SELECT`, возвращает список словарей.
- **`create(table, row: dict, returning=None)`** — `INSERT` одной строки; при `returning` — одна строка результата.
- **`update(table, data, where, where_params=None, returning=None)`** — `UPDATE`.
- **`delete(table, where, where_params=None, returning=None)`** — `DELETE`.

Ошибки выполнения в этих методах логируются в консоль; при неудаче `create` / `update` / `delete` делается `rollback`.

## Быстрый пример (отдельный скрипт)

После настройки `.env` и создания таблиц через `backend.py`:

```python
from postgres_driver import PostgresDriver

with PostgresDriver() as db:
    if not db.connection:
        print("Не удалось подключиться")
    else:
        rows = db.read("users", order_by="user_id DESC", limit=5)
        print(rows)
```

Для полного сценария (GUI, пользователи, столы, брони) используйте **`python app.py`** — см. [README.MD](README.MD).
