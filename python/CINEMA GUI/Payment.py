import tkinter as tk
from tkinter import Label, Frame, Button, Toplevel, StringVar, messagebox
from PIL import Image, ImageTk
from datetime import datetime
import mysql.connector
from mysql.connector import Error

class CustomerFormApp(tk.Toplevel):
    def __init__(self, parent, db_connection, screening_id, selected_seats, total_price):
        super().__init__(parent)
        self.parent = parent
        self.title("Customer Form")
        self.geometry("800x500")
        self.mydb = db_connection
        self.screening_id = screening_id
        self.selected_seats = selected_seats
        self.total_price = total_price
        self.amount_due_var = StringVar(value=f"{self.total_price:.2f}")
        self.create_widgets()


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
            price = float(self.total_price)
            discount_text = self.discount_entry.get().strip()
            discount = float(discount_text) if discount_text else 0.0

            discount = min(max(discount, 0), 100)
            if float(discount_text or 0) != discount:
                self.discount_entry.delete(0, tk.END)
                self.discount_entry.insert(0, str(discount))

            amount_due = price * (100 - discount) / 100
            self.amount_due_var.set(f"{amount_due:.2f}")
        except ValueError:
            self.amount_due_var.set(f"{self.total_price:.2f}")


    def confirm_form(self):
        customer_name = self.customer_name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        day = self.day_entry.get().strip()
        month = self.month_entry.get().strip()
        year = self.year_entry.get().strip()
        dob = f"{year}-{month.zfill(2)}-{day.zfill(2)}" if day and month and year else None
        screening_id = self.screening_id
        amount_due = float(self.amount_due_var.get())
        

        self.book_ticket_and_insert_payment(customer_name, dob, phone, screening_id, self.selected_seats, amount_due)

        if not customer_name or not phone:
            self.error_label.config(text="Please enter customer name and phone number!")
            return
        else:
            self.error_label.config(text="")


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
            self.discount_entry.config(state="normal")
            self.discount_entry.delete(0, tk.END)
            self.discount_entry.config(state="readonly")
            self.calculate_amount_due()
            
    def book_ticket_and_insert_payment(self, customer_name, dob, phone, screening_id, selected_seats, amount_due):
        try:
            cursor = self.mydb.cursor()
            ticket_ids = []
    
            for seat in selected_seats:
                result = ''
                cursor.callproc("ticket_booking", (customer_name, phone, dob, screening_id, seat, result))
    
                for res in cursor.stored_results():
                    result = res.fetchone()[0]
    
                if "successfully" not in result.lower():
                    messagebox.showerror("Booking Failed", f"{seat}: {result}")
                    return  # Exit on first failure
    
                # Get IDs for payment
                cursor.execute("SELECT CustomerID FROM Customers WHERE PhoneNumber = %s", (phone,))
                customer_id = cursor.fetchone()[0]
    
                cursor.execute("SELECT RoomID FROM Screenings WHERE ScreeningID = %s", (screening_id,))
                room_id = cursor.fetchone()[0]
    
                cursor.execute("SELECT SeatID FROM Seats WHERE RoomID = %s AND SeatNumber = %s", (room_id, seat))
                seat_id = cursor.fetchone()[0]
    
                cursor.execute("""
                    SELECT TicketID FROM Tickets 
                    WHERE CustomerID = %s AND ScreeningID = %s AND SeatID = %s
                    ORDER BY TicketID DESC LIMIT 1
                """, (customer_id, screening_id, seat_id))
                ticket_id = cursor.fetchone()[0]
                ticket_ids.append(ticket_id)
    
            # Insert payments for each ticket
            for ticket_id in ticket_ids:
                cursor.execute("""
                    INSERT INTO Payments (CustomerID, ScreeningID, TicketID, Amount, PayTime)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (customer_id, screening_id, ticket_id, amount_due/len(ticket_ids)))
    
            self.mydb.commit()
            messagebox.showinfo("Success", f"Tickets for {len(selected_seats)} seat(s) booked successfully!")
    
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            cursor.close()

    def create_widgets(self):
        #Confirm button
        Button(self, text="Confirm", font=("Arial", 10), width=15, command=self.confirm_form).place(x=330, y=420)
        Button(self, text="BACK", font=("Arial", 10), width=7).place(x=10, y=10)
        
        #Customer name
        Label(self, text="Customer Name:").place(x=80, y=100)
        vcmd_name = (self.register(self.validate_name_input), '%P')
        self.customer_name_entry = tk.Entry(self, width=40, validate='key', validatecommand = vcmd_name)
        self.customer_name_entry.place(x=250, y=100)
        
        #Phone number
        Label(self, text="Phone Number:").place(x=80, y=150)
        vcmd_phone = (self.register(self.validate_phone_input), '%P')
        self.phone_entry = tk.Entry(self, width=40, validate='key', validatecommand = vcmd_phone)
        self.phone_entry.place(x=250, y=150)
        
        #DOB
        Label(self, text="DOB - optional:").place(x=80, y=200)
        self.day_entry = tk.Entry(self, width=3, validate='key', validatecommand=(self.register(self.validate_day_input), '%P'))
        self.day_entry.place(x=250, y=200)
        Label(self, text="/").place(x=275, y=200)
        self.month_entry = tk.Entry(self, width=3, validate='key', validatecommand=(self.register(self.validate_month_input), '%P'))
        self.month_entry.place(x=285, y=200)
        Label(self, text="/").place(x=310, y=200)
        self.year_entry = tk.Entry(self, width=5, validate='key', validatecommand=(self.register(self.validate_year_input), '%P'))
        self.year_entry.place(x=320, y=200)
        
        #Seat number
        Label(self, text="Seat Number:").place(x=80, y=250)
        self.seat_entry = tk.Entry(self, width=20, state="normal")
        self.seat_entry.place(x=250, y=250)
        seats_str = ", ".join(self.selected_seats.keys())
        self.seat_entry.insert(0, seats_str)
        self.seat_entry.configure(state="readonly")
        
        
        #Price        
        Label(self, text="Price (VND):").place(x=500, y=260)
        self.price_entry = tk.Entry(self, width=20, state="normal")
        self.price_entry.place(x=610, y=260)
        self.price_entry.insert(0, f"{self.total_price:.2f}")
        self.price_entry.configure(state="readonly")

        Label(self, text="Discount (%):").place(x=500, y=300)
        self.discount_entry = tk.Entry(self, width=20, state="readonly")
        self.discount_entry.place(x=610, y=300)

        Label(self, text="Amount Due (VND):").place(x=500, y=340)
        Label(self, textvariable=self.amount_due_var, width=18, relief="sunken", bg="white", anchor="w").place(x=610, y=340)

        self.price_entry.bind('<KeyRelease>', self.calculate_amount_due)
        self.discount_entry.bind('<KeyRelease>', self.calculate_amount_due)
        self.price_entry.bind('<FocusOut>', self.calculate_amount_due)
        self.discount_entry.bind('<FocusOut>', self.calculate_amount_due)

        self.calculate_amount_due()

        self.error_label = Label(self, text="", fg="red", font=("Arial", 10))
        self.error_label.place(x=250, y=390)

        self.day_entry.bind('<FocusOut>', self.check_auto_discount)
        self.month_entry.bind('<FocusOut>', self.check_auto_discount)
        self.year_entry.bind('<FocusOut>', self.check_auto_discount)

if __name__ == "__main__":
    app=CustomerFormApp()
    app.mainloop()