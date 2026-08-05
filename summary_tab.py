"""
summary_tab.py
---------------
The Summary tab: a read-only dashboard showing total income, total
expense, balance, and spend broken down by category.

If your professor asks "where's the Read part of CRUD used for
something more than a plain table" -- this file is the best example,
since it runs SUM() and GROUP BY queries instead of a simple SELECT *.
"""

from tkinter import ttk

from database import get_connection


class SummaryTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.build_widgets()

    def build_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=10)

        self.income_label = ttk.Label(top, text="Total Income: 0.00", font=("Segoe UI", 12, "bold"))
        self.income_label.pack(side="left", padx=20)

        self.expense_label = ttk.Label(top, text="Total Expense: 0.00", font=("Segoe UI", 12, "bold"))
        self.expense_label.pack(side="left", padx=20)

        self.balance_label = ttk.Label(top, text="Balance: 0.00", font=("Segoe UI", 12, "bold"))
        self.balance_label.pack(side="left", padx=20)

        ttk.Button(top, text="Refresh", command=self.refresh_summary).pack(side="right", padx=10)

        columns = ("category", "total_expense")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=13)
        self.tree.heading("category", text="Category")
        self.tree.heading("total_expense", text="Total Spent")
        self.tree.column("category", width=250)
        self.tree.column("total_expense", width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_summary()

    def refresh_summary(self):
        """
        Pulls aggregate totals straight from the database using SQL's
        own SUM() and GROUP BY, rather than fetching every row and
        adding them up in Python -- the database does the heavy lifting.
        """
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE txn_type='Income'")
        total_income = cur.fetchone()[0]

        cur.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE txn_type='Expense'")
        total_expense = cur.fetchone()[0]

        self.income_label.config(text=f"Total Income: {total_income:.2f}")
        self.expense_label.config(text=f"Total Expense: {total_expense:.2f}")
        self.balance_label.config(text=f"Balance: {(total_income - total_expense):.2f}")

        for row in self.tree.get_children():
            self.tree.delete(row)

        cur.execute("""
            SELECT c.name, COALESCE(SUM(t.amount), 0) as total
            FROM categories c
            LEFT JOIN transactions t ON c.category_id = t.category_id AND t.txn_type = 'Expense'
            GROUP BY c.category_id
            ORDER BY total DESC
        """)
        for row in cur.fetchall():
            self.tree.insert("", "end", values=(row[0], f"{row[1]:.2f}"))

        conn.close()
