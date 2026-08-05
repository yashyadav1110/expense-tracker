"""
transactions_tab.py
--------------------
The Transactions tab: add, view, update, and delete income/expense
entries. Each transaction links to a category from categories_tab.py.

If your professor asks about the main data-entry screen, or how
adding an expense actually gets saved -- this is the file to open.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from database import get_connection


class TransactionsTab(ttk.Frame):
    def __init__(self, parent, categories_tab):
        super().__init__(parent)
        self.categories_tab = categories_tab  # reference so we can read the category list
        self.selected_id = None
        self.build_form()
        self.build_table()
        self.refresh_dropdown()
        self.refresh_table()

    # -----------------------------------------------------------------
    # UI SETUP
    # -----------------------------------------------------------------

    def build_form(self):
        form = ttk.LabelFrame(self, text="Transaction Details")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Type:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.type_combo = ttk.Combobox(form, width=15, state="readonly", values=["Expense", "Income"])
        self.type_combo.current(0)
        self.type_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form, text="Category:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.category_combo = ttk.Combobox(form, width=20, state="readonly")
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(form, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(form, width=18)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form, text="Date (YYYY-MM-DD):").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(form, width=20)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(form, text="Note:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.note_entry = ttk.Entry(form, width=50)
        self.note_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=3, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="Refresh Categories", command=self.refresh_dropdown).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Add Transaction", command=self.add_transaction).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_transaction).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_transaction).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).grid(row=0, column=4, padx=5)

    def build_table(self):
        columns = ("id", "type", "category", "amount", "date", "note")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=13)
        headers = ["ID", "Type", "Category", "Amount", "Date", "Note"]
        widths = [40, 80, 120, 90, 100, 250]
        for col, label, w in zip(columns, headers, widths):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=w)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def refresh_dropdown(self):
        """Pulls the current category list from categories_tab.py."""
        self.category_map = {name: cid for cid, name in self.categories_tab.get_all_categories()}
        self.category_combo["values"] = list(self.category_map.keys())

    # -----------------------------------------------------------------
    # CREATE
    # -----------------------------------------------------------------

    def add_transaction(self):
        txn_type = self.type_combo.get()
        category_name = self.category_combo.get()
        amount = self.amount_entry.get().strip()
        txn_date = self.date_entry.get().strip()
        note = self.note_entry.get().strip()

        if not category_name or not amount or not txn_date:
            messagebox.showerror("Missing Data", "Type, Category, Amount and Date are required.")
            return
        try:
            amount_val = float(amount)
        except ValueError:
            messagebox.showerror("Invalid Data", "Amount must be a number.")
            return

        category_id = self.category_map[category_name]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO transactions (category_id, txn_type, amount, txn_date, note) VALUES (?, ?, ?, ?, ?)",
            (category_id, txn_type, amount_val, txn_date, note),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Transaction added successfully.")
        self.clear_form()
        self.refresh_table()

    # -----------------------------------------------------------------
    # READ
    # -----------------------------------------------------------------

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT t.txn_id, t.txn_type, c.name, t.amount, t.txn_date, t.note
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            ORDER BY t.txn_date DESC
        """)
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    # -----------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------

    def update_transaction(self):
        if self.selected_id is None:
            messagebox.showerror("No Selection", "Select a transaction from the table to update.")
            return

        txn_type = self.type_combo.get()
        category_name = self.category_combo.get()
        amount = self.amount_entry.get().strip()
        txn_date = self.date_entry.get().strip()
        note = self.note_entry.get().strip()

        if not category_name or not amount or not txn_date:
            messagebox.showerror("Missing Data", "Type, Category, Amount and Date are required.")
            return
        try:
            amount_val = float(amount)
        except ValueError:
            messagebox.showerror("Invalid Data", "Amount must be a number.")
            return

        category_id = self.category_map[category_name]

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE transactions SET category_id=?, txn_type=?, amount=?, txn_date=?, note=? WHERE txn_id=?",
            (category_id, txn_type, amount_val, txn_date, note, self.selected_id),
        )
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Transaction updated successfully.")
        self.clear_form()
        self.refresh_table()

    # -----------------------------------------------------------------
    # DELETE
    # -----------------------------------------------------------------

    def delete_transaction(self):
        if self.selected_id is None:
            messagebox.showerror("No Selection", "Select a transaction from the table to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?")
        if not confirm:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM transactions WHERE txn_id=?", (self.selected_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Transaction deleted successfully.")
        self.clear_form()
        self.refresh_table()

    # -----------------------------------------------------------------
    # HELPERS
    # -----------------------------------------------------------------

    def on_row_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        self.selected_id = values[0]
        self.type_combo.set(values[1])
        self.category_combo.set(values[2])
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, values[3])
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, values[4])
        self.note_entry.delete(0, tk.END)
        self.note_entry.insert(0, values[5])

    def clear_form(self):
        self.selected_id = None
        self.type_combo.current(0)
        self.category_combo.set("")
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date.today().isoformat())
        self.note_entry.delete(0, tk.END)
