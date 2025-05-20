import tkinter as tk
from tkinter import Label, Frame, Button, Toplevel
from PIL import Image, ImageTk

def calculate_amount_due():
    try:
        price = float(price_entry.get())
        discount = float(discount_entry.get())
        amount_due = price - discount
        amount_due_entry.delete(0, tk.END)
        amount_due_entry.insert(0, f"{amount_due:.2f}")
    except ValueError:
        amount_due_entry.delete(0, tk.END)
        amount_due_entry.insert(0, "Invalid input")

root = tk.Tk()
root.title("Customer Form")
root.geometry("800x500")

back_button = Button(root, text="BACK",font=10, width=7, height=1)
back_button.place(x=10, y=10)

#Customer_name,Phone_Number,DOB
Label(root, text="Customer Name:").place(x=80, y=100)
customer_name_entry = tk.Entry(root, width=40)
customer_name_entry.place(x=250, y=100)

Label(root, text="Phone Number:").place(x=80, y=150)
phone_entry = tk.Entry(root, width=40)
phone_entry.place(x=250, y=150)

Label(root, text="DOB (optional):").place(x=80, y=200)
dob_entry = tk.Entry(root, width=40)
dob_entry.place(x=250, y=200)

#Price,Discount,Amount Due
Label(root, text="Price:").place(x=500, y=260)
price_entry = tk.Entry(root, width=20)
price_entry.place(x=600, y=260)

Label(root, text="Discount:").place(x=500, y=300)
discount_entry = tk.Entry(root, width=20)
discount_entry.place(x=600, y=300)

Label(root, text="Amount Due:").place(x=500, y=340)
amount_due_entry = tk.Entry(root, width=20)
amount_due_entry.place(x=600, y=340)

complete_button = Button(root, text="Confirm",font=10, width=15, command=calculate_amount_due)
complete_button.place(x=330, y=420)

root.mainloop()
