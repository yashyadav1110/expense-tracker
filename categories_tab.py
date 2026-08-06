import tkinter as tk
from tkinter import ttk, messagebox
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from database import get_db


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

        db = get_db()
        try:
            db.categories.insert_one({"name": name})
        except DuplicateKeyError:
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

        db = get_db()
        for doc in db.categories.find().sort("name", 1):
            self.tree.insert("", "end", values=(str(doc["_id"]), doc["name"]))

    def get_all_categories(self):
        
        db = get_db()
        return [(str(doc["_id"]), doc["name"]) for doc in db.categories.find().sort("name", 1)]

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

        db = get_db()
        try:
            db.categories.update_one(
                {"_id": ObjectId(self.selected_id)},
                {"$set": {"name": name}},
            )
        except DuplicateKeyError:
            messagebox.showerror("Duplicate", "That category already exists.")
            return

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

        db = get_db()
        db.categories.delete_one({"_id": ObjectId(self.selected_id)})

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