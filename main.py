import tkinter as tk
from tkinter import ttk

from database import init_db
from categories_tab import CategoriesTab
from transactions_tab import TransactionsTab
from summary_tab import SummaryTab


class ExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Personal Expense Tracker")
        self.geometry("950x620")
        self.resizable(True, True)

        # Create Notebook (Tabs)
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create Tabs
        self.categories_tab = CategoriesTab(notebook)
        self.transactions_tab = TransactionsTab(notebook, self.categories_tab)
        self.summary_tab = SummaryTab(notebook)

        # Add Tabs
        notebook.add(self.transactions_tab, text="Transactions")
        notebook.add(self.categories_tab, text="Categories")
        notebook.add(self.summary_tab, text="Summary")

        # Refresh summary whenever Summary tab is opened
        notebook.bind(
            "<<NotebookTabChanged>>",
            lambda event: self.summary_tab.refresh_summary()
        )


if __name__ == "__main__":
    try:
        init_db()
        print("Database connected successfully.")
    except Exception as e:
        print(f"Database connection failed: {e}")

    app = ExpenseApp()
    app.mainloop()