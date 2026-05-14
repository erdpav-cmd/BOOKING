"""
Графический интерфейс для системы бронирования (полная версия).
"""
import tkinter as tk
from tkinter import ttk, messagebox
import backend

class BookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Система бронирования ресторана")
        self.root.geometry("800x600")

        # Создаем вкладки
        tab_control = ttk.Notebook(root)

        self.tab_users = ttk.Frame(tab_control)
        self.tab_tables = ttk.Frame(tab_control)
        self.tab_bookings = ttk.Frame(tab_control)

        tab_control.add(self.tab_users, text='Пользователи')
        tab_control.add(self.tab_tables, text='Столы')
        tab_control.add(self.tab_bookings, text='Бронирование')

        tab_control.pack(expand=1, fill="both")

        # Сначала создаем ВСЕ виджеты на всех вкладках
        self.setup_users_tab()
        self.setup_tables_tab()
        self.setup_bookings_tab()
        
        # И только потом загружаем данные
        self.refresh_users_list()
        self.refresh_tables_list()

    # ================= USERS TAB =================
    def setup_users_tab(self):
        frame = ttk.LabelFrame(self.tab_users, text="Добавить пользователя")
        frame.pack(fill="x", padx=10, pady=5)

        # Email
        ttk.Label(frame, text="Email:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.user_email = ttk.Entry(frame)
        self.user_email.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Password
        ttk.Label(frame, text="Пароль:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.user_pass = ttk.Entry(frame, show="*")
        self.user_pass.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # First Name
        ttk.Label(frame, text="Имя:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.user_fname = ttk.Entry(frame)
        self.user_fname.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # Last Name
        ttk.Label(frame, text="Фамилия:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.user_lname = ttk.Entry(frame)
        self.user_lname.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        # Phone
        ttk.Label(frame, text="Телефон:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.user_phone = ttk.Entry(frame)
        self.user_phone.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        # Role
        ttk.Label(frame, text="Роль:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.user_role = ttk.Combobox(frame, values=["user", "manager", "admin"], state="readonly")
        self.user_role.current(0)
        self.user_role.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        # Status
        ttk.Label(frame, text="Статус:").grid(row=6, column=0, sticky="w", padx=5, pady=2)
        self.user_status = ttk.Combobox(frame, values=["active", "inactive", "blocked", "pending"], state="readonly")
        self.user_status.current(0)
        self.user_status.grid(row=6, column=1, sticky="ew", padx=5, pady=2)

        frame.columnconfigure(1, weight=1)

        ttk.Button(self.tab_users, text="Добавить пользователя", command=self.add_user).pack(pady=10)
        ttk.Button(self.tab_users, text="Обновить список", command=self.refresh_users_list).pack()
        
        # Список пользователей (Treeview для красоты)
        cols = ("ID", "Email", "Name", "Role", "Status")
        self.users_tree = ttk.Treeview(self.tab_users, columns=cols, show="headings")
        for col in cols:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
        self.users_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def add_user(self):
        result = backend.create_user(
            email=self.user_email.get(),
            password_hash=self.user_pass.get(),
            first_name=self.user_fname.get(),
            last_name=self.user_lname.get(),
            phone=self.user_phone.get(),
            role=self.user_role.get(),
            status=self.user_status.get()
        )
        if result:
            messagebox.showinfo("Успех", "Пользователь добавлен")
            self.refresh_users_list()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить")

    def refresh_users_list(self):
        for i in self.users_tree.get_children():
            self.users_tree.delete(i)
        users = backend.get_all_users()
        for u in users:
            self.users_tree.insert("", "end", values=(
                u['user_id'], u['email'], f"{u['first_name']} {u['last_name']}", 
                u['role'], u['status']
            ))
        self.update_booking_comboboxes()

    # ================= TABLES TAB =================
    def setup_tables_tab(self):
        frame = ttk.LabelFrame(self.tab_tables, text="Добавить стол")
        frame.pack(fill="x", padx=10, pady=5)

        # Table Number
        ttk.Label(frame, text="Номер стола:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.table_number = ttk.Entry(frame)
        self.table_number.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Capacity
        ttk.Label(frame, text="Вместимость:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.table_cap = ttk.Entry(frame)
        self.table_cap.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Location
        ttk.Label(frame, text="Расположение:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.table_loc = ttk.Combobox(frame, values=["main_hall", "terrace", "vip_room"], state="readonly")
        self.table_loc.current(0)
        self.table_loc.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # Status
        ttk.Label(frame, text="Статус:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.table_status = ttk.Combobox(frame, values=["available", "occupied", "reserved", "cleaning", "broken"], state="readonly")
        self.table_status.current(0)
        self.table_status.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        # Description
        ttk.Label(frame, text="Описание:").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.table_desc = ttk.Entry(frame)
        self.table_desc.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        # Hourly Rate
        ttk.Label(frame, text="Цена/час:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.table_rate = ttk.Entry(frame)
        self.table_rate.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        # Checkboxes
        self.table_window = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Вид из окна", variable=self.table_window).grid(row=6, column=0, columnspan=2, sticky="w", padx=5)

        self.table_smoking = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Курение разрешено", variable=self.table_smoking).grid(row=7, column=0, columnspan=2, sticky="w", padx=5)

        frame.columnconfigure(1, weight=1)

        ttk.Button(self.tab_tables, text="Добавить стол", command=self.add_table).pack(pady=10)
        ttk.Button(self.tab_tables, text="Обновить список", command=self.refresh_tables_list).pack()
        
        cols = ("ID", "Number", "Cap", "Loc", "Status", "Desc")
        self.tables_tree = ttk.Treeview(self.tab_tables, columns=cols, show="headings")
        for col in cols:
            self.tables_tree.heading(col, text=col)
            self.tables_tree.column(col, width=80)
        self.tables_tree.pack(fill="both", expand=True, padx=10, pady=10)

    def add_table(self):
        try:
            hourly_rate = float(self.table_rate.get()) if self.table_rate.get() else None
        except ValueError:
            hourly_rate = None
            
        result = backend.create_table(
            table_number=self.table_number.get(),
            capacity=int(self.table_cap.get()),
            location=self.table_loc.get(),
            status=self.table_status.get(),
            description=self.table_desc.get(),
            hourly_rate=hourly_rate,
            has_window_view=self.table_window.get(),
            is_smoking_allowed=self.table_smoking.get()
        )
        if result:
            messagebox.showinfo("Успех", "Стол добавлен")
            self.refresh_tables_list()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить")

    def refresh_tables_list(self):
        for i in self.tables_tree.get_children():
            self.tables_tree.delete(i)
        tables = backend.get_all_tables()
        for t in tables:
            self.tables_tree.insert("", "end", values=(
                t['table_id'], t['table_number'], t['capacity'], 
                t['location'], t['status'], t['description']
            ))
        self.update_booking_comboboxes()

    # ================= BOOKINGS TAB =================
    def setup_bookings_tab(self):
        frame = ttk.LabelFrame(self.tab_bookings, text="Новое бронирование")
        frame.pack(fill="x", padx=10, pady=5)

        # User
        ttk.Label(frame, text="Пользователь:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.booking_user = ttk.Combobox(frame, state="readonly")
        self.booking_user.grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        # Table
        ttk.Label(frame, text="Стол:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.booking_table = ttk.Combobox(frame, state="readonly")
        self.booking_table.grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        # Date
        ttk.Label(frame, text="Дата (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.booking_date = ttk.Entry(frame)
        self.booking_date.insert(0, "2026-05-14")
        self.booking_date.grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        # Start Time
        ttk.Label(frame, text="Начало (HH:MM):").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.booking_start = ttk.Entry(frame)
        self.booking_start.insert(0, "18:00")
        self.booking_start.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        # End Time
        ttk.Label(frame, text="Конец (HH:MM):").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        self.booking_end = ttk.Entry(frame)
        self.booking_end.insert(0, "20:00")
        self.booking_end.grid(row=4, column=1, sticky="ew", padx=5, pady=2)

        # Guests
        ttk.Label(frame, text="Гостей:").grid(row=5, column=0, sticky="w", padx=5, pady=2)
        self.booking_guests = ttk.Entry(frame)
        self.booking_guests.insert(0, "2")
        self.booking_guests.grid(row=5, column=1, sticky="ew", padx=5, pady=2)

        frame.columnconfigure(1, weight=1)

        ttk.Button(self.tab_bookings, text="Проверить и забронировать", 
                   command=self.create_booking).pack(pady=15, ipadx=20, ipady=5)

    def update_booking_comboboxes(self):
        # Проверяем, что атрибуты существуют
        if not hasattr(self, 'booking_user') or not hasattr(self, 'booking_table'):
            return
            
        # Обновляем списки выбора в вкладке Бронирование
        users = backend.get_all_users()
        if users:
            user_opts = [f"{u['user_id']} - {u['email']}" for u in users if u.get('user_id')]
            self.booking_user['values'] = user_opts
            if user_opts: 
                self.booking_user.current(0)
        else:
            self.booking_user['values'] = ["Сначала создайте пользователей"]
            self.booking_user.current(0)
        
        tables = backend.get_all_tables()
        if tables:
            table_opts = [f"{t['table_id']} - Стол №{t['table_number']}" for t in tables if t.get('table_id')]
            self.booking_table['values'] = table_opts
            if table_opts: 
                self.booking_table.current(0)
        else:
            self.booking_table['values'] = ["Сначала создайте столы"]
            self.booking_table.current(0)

    def create_booking(self):
        user_val = self.booking_user.get()
        table_val = self.booking_table.get()
        
        # Проверка на пустые значения или "None"
        if not user_val or user_val == "None" or not table_val or table_val == "None":
            messagebox.showwarning("Внимание", "Выберите пользователя и стол из списков!\n"
                                  "Если списки пустые, сначала создайте пользователей и столы.")
            return

        try:
            user_id = int(user_val.split(" - ")[0])
            table_id = int(table_val.split(" - ")[0])
        except (ValueError, IndexError) as e:
            messagebox.showerror("Ошибка", f"Не удалось распознать выбранные значения.\n"
                                f"Пользователь: {user_val}\nСтол: {table_val}")
            return
        
        date = self.booking_date.get()
        start = self.booking_start.get()
        end = self.booking_end.get()
        
        try:
            guests = int(self.booking_guests.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Количество гостей должно быть числом")
            return
        
        # Создаем бронь
        result = backend.create_booking(user_id, table_id, date, start, end, guests)
        
        if result:
            messagebox.showinfo("Успех", "Бронирование создано!")
        else:
            messagebox.showwarning("Занято", "Это время уже забронировано или произошла ошибка!")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookingApp(root)
    root.mainloop()