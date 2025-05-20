import tkinter as tk
from tkinter import Label, Frame, Button, Toplevel, StringVar
from PIL import Image, ImageTk
from datetime import datetime
import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "admin",
    password = "quang123",
    database="cinema_management"
)

def validate_day_input(text):
    if text == "":
        return True
    if not text.isdigit():
        return False
    if len(text) > 2:
        return False
    if len(text) == 2:
        day = int(text)
        return 1 <= day <= 31
    return True
def validate_month_input(text):
    if text == "":
        return True
    if not text.isdigit():
        return False
    if len(text) > 2:
        return False
    if len(text) == 2:
        month = int(text)
        return 1 <= month <= 12
    return True
def validate_year_input(text):
    if text == "":
        return True
    if not text.isdigit():
        return False
    if len(text) > 4:
        return False
    return True

def calculate_amount_due(*args):
    try:
        price_text = price_entry.get().strip()
        discount_text = discount_entry.get().strip()

        price = 0.0
        discount = 0.0

        if price_text:
            price = float(price_text)

        if discount_text:
            discount = float(discount_text)
            if discount < 0:
                discount = 0
            elif discount > 100:
                discount = 100
                discount_entry.delete(0, tk.END)
                discount_entry.insert(0, "100")

        amount_due = price * (100 - discount) / 100

        amount_due_var.set(f"{amount_due:.2f}")

    except ValueError:
        amount_due_var.set("0.00")


def confirm_form():
    day = day_entry.get().strip()
    month = month_entry.get().strip()
    year = year_entry.get().strip()

    dob = ""
    if day or month or year:
        dob = f"{day:0>2}/{month:0>2}/{year}" if day and month and year else f"{day}/{month}/{year}"

root = tk.Tk()
root.title("Customer Form")
root.geometry("800x500")

#button
complete_button = Button(root, text="Confirm", font=("Arial", 10), width=15, command=confirm_form)
complete_button.place(x=330, y=420)
back_button = Button(root, text="BACK", font=("Arial", 10), width=7, height=1)
back_button.place(x=10, y=10)

#label
Label(root, text="Customer Name:").place(x=80, y=100)
customer_name_entry = tk.Entry(root, width=40)
customer_name_entry.place(x=250, y=100)

Label(root, text="Phone Number:").place(x=80, y=150)
phone_entry = tk.Entry(root, width=40)
phone_entry.place(x=250, y=150)

dob_label = Label(root, text="DOB - optional:")
dob_label.place(x=80, y=200)
day_vcmd = (root.register(validate_day_input), '%P')
day_entry = tk.Entry(root, width=3, validate='key', validatecommand=day_vcmd)
day_entry.place(x=250, y=200)
slash1_label = Label(root, text="/")
slash1_label.place(x=275, y=200)
month_vcmd = (root.register(validate_month_input), '%P')
month_entry = tk.Entry(root, width=3, validate='key', validatecommand=month_vcmd)
month_entry.place(x=285, y=200)
slash2_label = Label(root, text="/")
slash2_label.place(x=310, y=200)
year_vcmd = (root.register(validate_year_input), '%P')
year_entry = tk.Entry(root, width=5, validate='key', validatecommand=year_vcmd)
year_entry.place(x=320, y=200)

Label(root, text="Price ($):").place(x=500, y=260)
price_entry = tk.Entry(root, width=20)
price_entry.place(x=600, y=260)

Label(root, text="Discount (%):").place(x=500, y=300)
discount_entry = tk.Entry(root, width=20)
discount_entry.place(x=600, y=300)

Label(root, text="Amount Due ($):").place(x=500, y=340)
amount_due_var = StringVar()
amount_due_var.set("0.00")
amount_due_display = Label(root, textvariable=amount_due_var, width=18,
                           relief="sunken", bg="white", anchor="w")
amount_due_display.place(x=600, y=340)
price_entry.bind('<KeyRelease>', calculate_amount_due)
discount_entry.bind('<KeyRelease>', calculate_amount_due)
price_entry.bind('<FocusOut>', calculate_amount_due)
discount_entry.bind('<FocusOut>', calculate_amount_due)
price_entry.insert(0, "")
discount_entry.insert(0, "")
calculate_amount_due()


root.mainloop()