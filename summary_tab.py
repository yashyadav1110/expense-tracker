from tkinter import ttk

from database import get_db


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
        db = get_db()

        income_agg = list(db.transactions.aggregate([
            {"$match": {"txn_type": "Income"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]))
        total_income = income_agg[0]["total"] if income_agg else 0

        expense_agg = list(db.transactions.aggregate([
            {"$match": {"txn_type": "Expense"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]))
        total_expense = expense_agg[0]["total"] if expense_agg else 0

        self.income_label.config(text=f"Total Income: {total_income:.2f}")
        self.expense_label.config(text=f"Total Expense: {total_expense:.2f}")
        self.balance_label.config(text=f"Balance: {(total_income - total_expense):.2f}")

        for row in self.tree.get_children():
            self.tree.delete(row)

        # Expense totals grouped by category_id (MongoDB has no JOIN,
        # so category names are attached afterward in Python)
        category_totals = list(db.transactions.aggregate([
            {"$match": {"txn_type": "Expense"}},
            {"$group": {"_id": "$category_id", "total": {"$sum": "$amount"}}},
        ]))
        totals_by_cat_id = {row["_id"]: row["total"] for row in category_totals}

        rows = []
        for cat in db.categories.find():
            cat_id = str(cat["_id"])
            total = totals_by_cat_id.get(cat_id, 0)
            rows.append((cat["name"], total))

        rows.sort(key=lambda r: r[1], reverse=True)
        for name, total in rows:
            self.tree.insert("", "end", values=(name, f"{total:.2f}"))