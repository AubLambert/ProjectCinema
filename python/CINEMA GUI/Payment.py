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
                port = 3307,
                user="ticket_clerk",
                password="dat123",
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
    def validate_name_input(self, text):
        return text == "" or all(char.isalpha() or char.isspace() for char in text)
    def validate_phone_input(self, text):
        return text == "" or text.isdigit()
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
        seat_number = self.seat_entry.get().strip()
        screening_id = int(self.screening_id_entry.get().strip())
        amount_due = float(self.amount_due_var.get())

        self.book_ticket_and_insert_payment(customer_name, phone, screening_id, seat_number, amount_due)

        if not customer_name or not phone:
            self.error_label.config(text="Please enter customer name and phone number!")
            return
        else:
            self.error_label.config(text="")

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

    def check_auto_discount(self, event=None):
        try:
            day = int(self.day_entry.get())
            month = int(self.month_entry.get())
            year = int(self.year_entry.get())

            today = datetime.today()
            dob = datetime(year, month, day)

            is_birthday = (dob.day == today.day and dob.month == today.month)
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            is_under18_or_over65 = (age <= 18 or age >= 65)

            if is_under18_or_over65 and is_birthday:
                discount = 25
            elif is_under18_or_over65:
                discount = 20
            elif is_birthday:
                discount = 15

            else:
                discount = None

            if discount is not None:
                self.discount_entry.config(state="normal")
                self.discount_entry.delete(0, tk.END)
                self.discount_entry.insert(0, str(discount))
                self.discount_entry.config(state="readonly")
            else:
                self.discount_entry.config(state="readonly")

            self.calculate_amount_due()

        except ValueError:
            pass

    def book_ticket_and_insert_payment(self, customer_name, phone, screening_id, seat_number, amount):
        try:
            result = ''
            cursor = self.mydb.cursor()

            # Gọi stored procedure ticket_booking
            cursor.callproc("ticket_booking", (customer_name, phone, screening_id, seat_number, result))

            # Lấy kết quả từ OUT param
            for res in cursor.stored_results():
                result = res.fetchone()[0]

            if "successfully" not in result.lower():
                messagebox.showerror("Booking Failed", result)
                return

            # Truy vấn các ID cần để insert payment
            cursor.execute("SELECT CustomerID FROM Customers WHERE PhoneNumber = %s", (phone,))
            customer_id = cursor.fetchone()[0]

            cursor.execute("SELECT RoomID FROM Screenings WHERE ScreeningID = %s", (screening_id,))
            room_id = cursor.fetchone()[0]

            cursor.execute("SELECT SeatID FROM Seats WHERE RoomID = %s AND SeatNumber = %s", (room_id, seat_number))
            seat_id = cursor.fetchone()[0]

            cursor.execute("""
                SELECT TicketID FROM Tickets 
                WHERE CustomerID = %s AND ScreeningID = %s AND SeatID = %s
                ORDER BY TicketID DESC LIMIT 1
            """, (customer_id, screening_id, seat_id))
            ticket_id = cursor.fetchone()[0]

            # Insert payment
            cursor.execute("""
                INSERT INTO Payments (CustomerID, ScreeningID, TicketID, Amount, PayTime)
                VALUES (%s, %s, %s, %s, NOW())
            """, (customer_id, screening_id, ticket_id, amount))

            self.mydb.commit()
            messagebox.showinfo("Success", "Ticket booked and payment saved successfully!")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()

    def create_widgets(self):
        Button(self, text="Confirm", font=("Arial", 10), width=15, command=self.confirm_form).place(x=330, y=420)
        Button(self, text="BACK", font=("Arial", 10), width=7).place(x=10, y=10)

        Label(self, text="Customer Name:").place(x=80, y=100)
        vcmd_name = (self.register(self.validate_name_input), '%P')
        self.customer_name_entry = tk.Entry(self, width=40, validate='key', validatecommand = vcmd_name)
        self.customer_name_entry.place(x=250, y=100)

        Label(self, text="Phone Number:").place(x=80, y=150)
        vcmd_phone = (self.register(self.validate_phone_input), '%P')
        self.phone_entry = tk.Entry(self, width=40, validate='key', validatecommand = vcmd_phone)
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
        Label(self, text="Seat Number:").place(x=80, y=250)
        self.seat_entry = tk.Entry(self, width=20, state="readonly")
        self.seat_entry.place(x=250, y=250)
        Label(self, text="Screening ID:").place(x=80, y=300)
        self.screening_id_entry = tk.Entry(self, width=20, state="readonly")
        self.screening_id_entry.place(x=250, y=300)
        Label(self, text="Price (VND):").place(x=500, y=260)
        self.price_entry = tk.Entry(self, width=20, state="readonly")
        self.price_entry.place(x=600, y=260)

        Label(self, text="Discount (%):").place(x=500, y=300)
        self.discount_entry = tk.Entry(self, width=20, state="readonly")
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

        self.error_label = Label(self, text="", fg="red", font=("Arial", 10))
        self.error_label.place(x=250, y=390)

        self.day_entry.bind('<FocusOut>', self.check_auto_discount)
        self.month_entry.bind('<FocusOut>', self.check_auto_discount)
        self.year_entry.bind('<FocusOut>', self.check_auto_discount)

if __name__ == "__main__":
    app=CustomerFormApp()
    app.mainloop()