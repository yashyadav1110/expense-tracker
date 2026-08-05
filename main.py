import tkinter as tk
from tkinter import ttk

from database import init_db
from categories_tab import CategoriesTab
from transactions_tab import TransactionsTab
from summary_tab import SummaryTab


class ExpenseApp(tk.Tk):
    def _init_(self):
        super()._init_()

        self.title("Personal Expense Tracker")
        self.geometry("950x620")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.categories_tab = CategoriesTab(notebook)
        self.transactions_tab = TransactionsTab(notebook, self.categories_tab)
        self.summary_tab = SummaryTab(notebook)

        notebook.add(self.transactions_tab, text="Transactions")
        notebook.add(self.categories_tab, text="Categories")
        notebook.add(self.summary_tab, text="Summary")

        notebook.bind(
            "<<NotebookTabChanged>>",
            lambda e: self.summary_tab.refresh_summary()
        )


if __name__ == "_main_":
    init_db()
    app = ExpenseApp()
    app.mainloop()