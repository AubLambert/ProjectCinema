import tkinter as tk
from tkinter import Label, Frame, Button, Toplevel, StringVar, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import mysql.connector
from mysql.connector import Error

class CustomerFormApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Customer Form")
        self.geometry("800x500")
        self.mydb = self.connect_db()
        self.amount_due_var = StringVar(value="0.00")
        self.create_widgets()

    def connect_db(self):
        try:
            return mysql.connector.connect(
                host="localhost",
                user="admin",
                password="quang123",
                database="cinema_management"
            )
        except mysql.connector.Error as err:
            messagebox.showerror("Database Connection Error", f"Error: {err}")
            return None

#wot da hell
    def validate_day_input(self, text):
        return text == "" or (text.isdigit() and len(text) <= 2 and (len(text) < 2 or 1 <= int(text) <= 31))
    def validate_month_input(self, text):
        return text == "" or (text.isdigit() and len(text) <= 2 and (len(text) < 2 or 1 <= int(text) <= 12))
    def validate_year_input(self, text):
        return text == "" or (text.isdigit() and len(text) <= 4)
    def calculate_amount_due(self, *args):
        try:
            price_text = self.price_entry.get().strip()
            discount_text = self.discount_entry.get().strip()
            price = float(price_text) if price_text else 0.0
            discount = float(discount_text) if discount_text else 0.0

            discount = min(max(discount, 0), 100)
            if float(discount_text or 0) != discount:
                self.discount_entry.delete(0, tk.END)
                self.discount_entry.insert(0, str(discount))

            amount_due = price * (100 - discount) / 100
            self.amount_due_var.set(f"{amount_due:.2f}")
        except ValueError:
            self.amount_due_var.set("0.00")


    def confirm_form(self):
        customer_name = self.customer_name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        day = self.day_entry.get().strip()
        month = self.month_entry.get().strip()
        year = self.year_entry.get().strip()
        dob = f"{year}-{month.zfill(2)}-{day.zfill(2)}" if day and month and year else None

        try:
            mycursor = self.mydb.cursor()
            sql = "INSERT INTO Customers (customername, phonenumber, dob) VALUES (%s, %s, %s)"
            mycursor.execute(sql, (customer_name, phone, dob))
            self.mydb.commit()
            messagebox.showinfo("Success", "Customer data inserted successfully.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            mycursor.close()
    def create_widgets(self):
        Button(self, text="Confirm", font=("Arial", 10), width=15, command=self.confirm_form).place(x=330, y=420)
        Button(self, text="BACK", font=("Arial", 10), width=7).place(x=10, y=10)

        Label(self, text="Customer Name:").place(x=80, y=100)
        self.customer_name_entry = tk.Entry(self, width=40)
        self.customer_name_entry.place(x=250, y=100)

        Label(self, text="Phone Number:").place(x=80, y=150)
        self.phone_entry = tk.Entry(self, width=40)
        self.phone_entry.place(x=250, y=150)

        Label(self, text="DOB - optional:").place(x=80, y=200)
        self.day_entry = tk.Entry(self, width=3, validate='key', validatecommand=(self.register(self.validate_day_input), '%P'))
        self.day_entry.place(x=250, y=200)
        Label(self, text="/").place(x=275, y=200)
        self.month_entry = tk.Entry(self, width=3, validate='key', validatecommand=(self.register(self.validate_month_input), '%P'))
        self.month_entry.place(x=285, y=200)
        Label(self, text="/").place(x=310, y=200)
        self.year_entry = tk.Entry(self, width=5, validate='key', validatecommand=(self.register(self.validate_year_input), '%P'))
        self.year_entry.place(x=320, y=200)

        Label(self, text="Price ($):").place(x=500, y=260)
        self.price_entry = tk.Entry(self, width=20)
        self.price_entry.place(x=600, y=260)

        Label(self, text="Discount (%):").place(x=500, y=300)
        self.discount_entry = tk.Entry(self, width=20)
        self.discount_entry.place(x=600, y=300)

        Label(self, text="Amount Due ($):").place(x=500, y=340)
        Label(self, textvariable=self.amount_due_var, width=18, relief="sunken", bg="white", anchor="w").place(x=600, y=340)

        self.price_entry.bind('<KeyRelease>', self.calculate_amount_due)
        self.discount_entry.bind('<KeyRelease>', self.calculate_amount_due)
        self.price_entry.bind('<FocusOut>', self.calculate_amount_due)
        self.discount_entry.bind('<FocusOut>', self.calculate_amount_due)

        self.price_entry.insert(0, "")
        self.discount_entry.insert(0, "")
        self.calculate_amount_due()

if __name__ == "__main__":
    app=CustomerFormApp()
    app.mainloop()