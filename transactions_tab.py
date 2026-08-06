import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from bson import ObjectId

from database import get_db


class TransactionsTab(ttk.Frame):
    def __init__(self, parent, categories_tab):
        super().__init__(parent)

        self.categories_tab = categories_tab
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

        category_id = self.category_map[category_name]  # string form of ObjectId

        db = get_db()
        db.transactions.insert_one({
            "category_id": category_id,
            "txn_type": txn_type,
            "amount": amount_val,
            "txn_date": txn_date,
            "note": note,
        })

        messagebox.showinfo("Success", "Transaction added successfully.")
        self.clear_form()
        self.refresh_table()

    # -----------------------------------------------------------------
    # READ
    # -----------------------------------------------------------------

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        db = get_db()
        # No JOIN in MongoDB -- build a lookup dict of category_id -> name
        category_names = {str(c["_id"]): c["name"] for c in db.categories.find()}

        for doc in db.transactions.find().sort("txn_date", -1):
            cat_name = category_names.get(doc["category_id"], "Unknown")
            self.tree.insert("", "end", values=(
                str(doc["_id"]),
                doc["txn_type"],
                cat_name,
                doc["amount"],
                doc["txn_date"],
                doc.get("note", ""),
            ))

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

        db = get_db()
        db.transactions.update_one(
            {"_id": ObjectId(self.selected_id)},
            {"$set": {
                "category_id": category_id,
                "txn_type": txn_type,
                "amount": amount_val,
                "txn_date": txn_date,
                "note": note,
            }},
        )

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

        db = get_db()
        db.transactions.delete_one({"_id": ObjectId(self.selected_id)})

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