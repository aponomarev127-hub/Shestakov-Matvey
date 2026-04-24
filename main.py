import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

# =========================
# CONFIG
# =========================
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://v6.exchangerate-api.com/v6/"
HISTORY_FILE = "history.json"

CURRENCIES = [
    "USD", "EUR", "GBP", "RUB",
    "KZT", "JPY", "CNY", "TRY"
]

# =========================
# APP
# =========================
class CurrencyConverterApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Currency Converter")
        self.window.geometry("900x600")

        self.history = []

        self.build_ui()
        self.load_history()

    def build_ui(self):
        top = tk.Frame(self.window)
        top.pack(pady=10)

        tk.Label(top, text="Из").grid(row=0, column=0)
        self.from_currency = ttk.Combobox(top, values=CURRENCIES, state="readonly", width=10)
        self.from_currency.grid(row=0, column=1, padx=5)
        self.from_currency.current(0)

        tk.Label(top, text="В").grid(row=0, column=2)
        self.to_currency = ttk.Combobox(top, values=CURRENCIES, state="readonly", width=10)
        self.to_currency.grid(row=0, column=3, padx=5)
        self.to_currency.current(1)

        tk.Label(top, text="Сумма").grid(row=0, column=4)
        self.amount_entry = tk.Entry(top, width=15)
        self.amount_entry.grid(row=0, column=5, padx=5)

        tk.Button(top, text="Конвертировать", command=self.convert).grid(row=0, column=6, padx=10)

        self.result_label = tk.Label(self.window, text="Результат появится здесь", font=("Arial", 14))
        self.result_label.pack(pady=10)

        # TABLE
        self.tree = ttk.Treeview(self.window, columns=("date","from","to","amount","result"), show="headings")

        for col, text in zip(self.tree["columns"], ["Дата","Из","В","Сумма","Результат"]):
            self.tree.heading(col, text=text)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Button(self.window, text="Сохранить историю", command=self.save_history).pack(pady=5)

    # =========================
    # API
    # =========================
    def get_rates(self, base):
        try:
            url = f"{BASE_URL}{API_KEY}/latest/{base}"
            response = requests.get(url)
            data = response.json()

            if data.get("result") == "success":
                return data["conversion_rates"]
            return None
        except:
            return None

    # =========================
    # CONVERT
    # =========================
    def convert(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Введите положительное число")
            return

        from_cur = self.from_currency.get()
        to_cur = self.to_currency.get()

        rates = self.get_rates(from_cur)

        if not rates:
            messagebox.showerror("Ошибка", "Не удалось получить курс")
            return

        result = round(amount * rates[to_cur], 2)

        self.result_label.config(text=f"{amount} {from_cur} = {result} {to_cur}")

        row = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": from_cur,
            "to": to_cur,
            "amount": amount,
            "result": result
        }

        self.history.append(row)
        self.update_table()
        self.save_history()

    # =========================
    # TABLE
    # =========================
    def update_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for r in self.history:
            self.tree.insert("", "end", values=(r["date"],r["from"],r["to"],r["amount"],r["result"]))

    # =========================
    # JSON
    # =========================
    def save_history(self):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=4)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        self.update_table()

# =========================
# RUN
# =========================
window = tk.Tk()
app = CurrencyConverterApp(window)
window.mainloop()
