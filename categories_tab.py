"""
categories_tab.py
------------------
The Categories tab: add, view, update, and delete spending categories.

If your professor asks about the Categories screen or how category
CRUD works -- this is the file to open.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from database import get_connection


class CategoriesTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_id = None
        self.build_form()
        self.build_table()
        self.refresh_table()

    # -----------------------------------------------------------------
    # UI SETUP
    # -----------------------------------------------------------------

    def build_form(self):
        form = ttk.LabelFrame(self, text="Category Details")
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.name_entry = ttk.Entry(form, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Add Category", command=self.add_category).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self.update_category).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_category).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).grid(row=0, column=3, padx=5)

    def build_table(self):
        columns = ("id", "name")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        for col, label in zip(columns, ["ID", "Category Name"]):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=200)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    # -----------------------------------------------------------------
    # CREATE
    # -----------------------------------------------------------------

    def add_category(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Missing Data", "Category name is required.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
        except Exception:
            messagebox.showerror("Duplicate", "That category already exists.")
            return

        messagebox.showinfo("Success", "Category added successfully.")
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
        cur.execute("SELECT category_id, name FROM categories ORDER BY name")
        for row in cur.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def get_all_categories(self):
        """Used by transactions_tab.py to populate the category dropdown."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT category_id, name FROM categories ORDER BY name")
        result = cur.fetchall()
        conn.close()
        return result

    # -----------------------------------------------------------------
    # UPDATE
    # -----------------------------------------------------------------

    def update_category(self):
        if self.selected_id is None:
            messagebox.showerror("No Selection", "Select a category from the table to update.")
            return

        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Missing Data", "Category name is required.")
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE categories SET name=? WHERE category_id=?", (name, self.selected_id))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Category updated successfully.")
        self.clear_form()
        self.refresh_table()

    # -----------------------------------------------------------------
    # DELETE
    # -----------------------------------------------------------------

    def delete_category(self):
        if self.selected_id is None:
            messagebox.showerror("No Selection", "Select a category from the table to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Deleting a category will not delete its transactions. Continue?",
        )
        if not confirm:
            return

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM categories WHERE category_id=?", (self.selected_id,))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Category deleted successfully.")
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
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])

    def clear_form(self):
        self.selected_id = None
        self.name_entry.delete(0, tk.END)
