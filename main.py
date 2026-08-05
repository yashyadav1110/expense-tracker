"""
main.py
-------
Entry point of the application. Run this file to start the app:

    python main.py

If your professor asks "where does the program start" or "how are
the three tabs put together" -- this is the file to open.

This file does NOT contain any database code or CRUD logic itself --
it only builds the window and plugs the three tab modules into it.
"""

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

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Build each tab. TransactionsTab needs a reference to
        # CategoriesTab so it can read the current category list.
        self.categories_tab = CategoriesTab(notebook)
        self.transactions_tab = TransactionsTab(notebook, self.categories_tab)
        self.summary_tab = SummaryTab(notebook)

        notebook.add(self.transactions_tab, text="Transactions")
        notebook.add(self.categories_tab, text="Categories")
        notebook.add(self.summary_tab, text="Summary")

        # Refresh the summary numbers whenever the user switches to that tab
        notebook.bind("<<NotebookTabChanged>>", lambda e: self.summary_tab.refresh_summary())


if __name__ == "__main__":
    init_db()          # create the database file and tables (database.py)
    app = ExpenseApp()  # build the window and tabs
    app.mainloop()      # start the GUI event loop
