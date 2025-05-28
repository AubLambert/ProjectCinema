import tkinter as tk
from tkinter import messagebox, font, Label, Frame, Button, Toplevel, StringVar
from PIL import Image, ImageTk
from datetime import datetime
from tkinter import ttk
import mysql.connector
from mysql.connector import Error
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from tkinter import filedialog
import os
import warnings
import ttkbootstrap as tb
from ttkbootstrap.constants import *


base_dir = os.path.dirname(__file__)
warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")
class Liemora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LIEMORA Cinema Login")
        self.geometry("700x500")
        self.resizable(False, False)
        self.mydb = None #!
        self.timeslot_window = None #!
        self.build_login_ui()

    def build_login_ui(self):
        #Đổi lại path của ảnh
        img_path = os.path.join(base_dir, "Images", "Cat.jpg")
        bg_image = Image.open(img_path).resize((700, 500), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        self.bg_photo = bg_photo

        canvas = tk.Canvas(self, width=650, height=450)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=bg_photo, anchor="nw")

        frame = tk.Frame(canvas, bd=2, relief="solid", padx=25, pady=25)
        canvas.create_window(350, 250, window=frame)

        tk.Label(frame, text="LIEMORA Cinema", font=("Helvetica", 14, "bold")).pack(pady=(0, 20))
        tk.Label(frame, text="Account").pack()
        self.account_entry = tk.Entry(frame, width=30)
        self.account_entry.pack(pady=5)

        tk.Label(frame, text="Password").pack()
        self.password_entry = tk.Entry(frame, show="*", width=30)
        self.password_entry.pack(pady=5)

        login_btn = tk.Button(frame, text="Login", width=10, command=self.login)
        login_btn.pack(pady=10)
        self.bind("<Return>", lambda e: self.login())

    def login(self):
        username = self.account_entry.get()
        password = self.password_entry.get()

        try:
            self.mydb = mysql.connector.connect(
                host='localhost',
                user=username,
                password=password,
                database='cinema_management'
            )
            if self.mydb.is_connected():
                messagebox.showinfo("Login Success", f"Welcome, {username}")
                self.withdraw()
                if username == "admin":
                    Admin(self)
                else:
                    staff_ui(self, username)
            else:
                messagebox.showerror("Login Failed", "Error Occurred")

        except Error as e:
            messagebox.showerror("Login Failed", f"Invalid username or password.\n\n{e}")

class staff_ui(tk.Toplevel):
    def __init__(self, main, username):
        super().__init__(main)
        self.main=main
        self.username=username
        self.title("Staff interface")
        self.geometry("500x500")
        self.configure(bg="white")
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.staff_interface()
    def on_close(self):
        if self.main.mydb.is_connected():
            self.main.mydb.close()
        self.destroy()
        self.main.destroy()
        
    def logout(self):
        if self.main.mydb.is_connected():
            self.main.mydb.close()
        self.destroy()
        self.main.account_entry.delete(0, tk.END)
        self.main.password_entry.delete(0, tk.END)
        self.main.deiconify()
        
    def go_to_booking(self):
        Movie(self.main, self.username)
        self.destroy()
        
    def go_to_searching(self):
        ticket_searching(self.main, self.username)
        self.destroy()
        
    def staff_interface(self):
        tk.Button(self, text="Logout", font=10, width=7, command=self.logout).grid(row=0, column=0, sticky="nw", padx=20, pady=20)
        top_frame = tk.Frame(self, bg="white")
        top_frame.place(x=190,y=100)
        option_frame = tk.Frame(self, bg="white")
        option_frame.place(x=191,y=200)
        #Welcome
        top_label = tk.Label(top_frame, text="Welcome", font=("bold",25),justify="center")
        top_label.pack(padx=5, pady=5)
        #Options
        search_btn = tk.Button(option_frame, text="Search ticket", font=("bold",15), justify="center",
                               command = self.go_to_searching)
        search_btn.pack(pady=10, ipadx=4)
        booking_btn = tk.Button(option_frame, text="Ticket booking", font=("bold", 15), justify="center",
                                command= self.go_to_booking)
        booking_btn.pack(pady=10)

#Ticket search
class ticket_searching(tk.Toplevel):
    def __init__(self, main,username):
        super().__init__(main)
        self.main = main
        self.username = username
        self.title("Ticket searching")
        self.geometry("960x600")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.search_interface()
    
    def on_close(self):
        if self.main.mydb.is_connected():
            self.main.mydb.close()
        self.destroy()
        self.main.destroy()  
        
    def back2(self):
        self.destroy()
        self.main.deiconify()
        
    def search_interface(self):
        back_btn = tk.Button(
            self, text="BACK", font=('Arial', 10), borderwidth=1, width=7, height=1,
            command= self.back2
        )
        back_btn.place(x=30, y=30)
        
        
        ### Searchbar with effect
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            self, textvariable=self.search_var, font=('Arial', 12), justify="center", relief='solid',fg ="grey",
            borderwidth=1, width=50
        )
        search_entry.place(x=230, y=65, width=500, height=30)
        search_entry.insert(0, "Type in phone number or ticketID")
        
        search_entry.bind('<FocusIn>', self.on_entry_click)
        search_entry.bind('<FocusOut>', self.on_focusout)
        search_entry.bind('<Return>', lambda event: self.search_ticket())
        
        search_btn = tk.Button(
            self, text="Search", font=('Arial', 10), bg='#007bff', fg='white', relief='solid',
            padx=20, pady=5, command= self.search_ticket
        )
        search_btn.place(x=750, y=65, width=80, height=30)
        
        # Result panel outer frame
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.place(x=79.5, y=130, width=800, height=320)
        
        # Outer canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.scrollbar_x = tk.Scrollbar(self.canvas_frame, orient='horizontal', command=self.canvas.xview)
        self.scrollbar_y = tk.Scrollbar(self.canvas_frame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set)
        
        self.scrollbar_x.pack(side='bottom', fill='x')
        self.scrollbar_y.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Container canvas
        self.scrollable_container = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0, 0), window=self.scrollable_container, anchor='nw')
        
        # Bind scroll region update
        self.scrollable_container.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Headings frame
        self.heading_frame = tk.Frame(self.scrollable_container, bg='white')
        self.heading_frame.grid(row=0, column=0, sticky='nw')
        
        headings = ["Ticket ID", "Customer Name", "Phone", "Movie", "Room", "Date", "Seat", "Time", "Price (VND)", "Payment Time", "Action"]
        for col, title in enumerate(headings):
            lbl = tk.Label(self.heading_frame, text=title, font=('Arial', 10, 'bold'),
                           borderwidth=1, relief='solid', width=17)
            lbl.grid(row=0, column=col, sticky='nsew')
        
        # Results frame
        self.inner_frame = tk.Frame(self.scrollable_container, bg='white')
        self.inner_frame.grid(row=1, column=0, sticky='nw')
        self.rows = []
    
            
    def on_entry_click(self, event):
        if self.search_var.get() == "Type in phone number or ticketID":
            self.search_var.set("")
            event.widget.config(fg='black')

    def on_focusout(self, event):
        if self.search_var.get() == "":
            self.search_var.set("Type in phone number or ticketID")
            event.widget.config(fg='grey')
            
    def clear_rows(self):
        for widgets in self.rows:
            for w in widgets:
                w.destroy()
        self.rows.clear()
        
        
    # Find customer's ticket through input
    def search_ticket(self):
        user_input = self.search_var.get().strip()
        try:
            mycursor= self.main.mydb.cursor()
            query = """
            SELECT t.TicketID, c.CustomerName, c.PhoneNumber, m.MovieTitle, r.RoomName, se.SeatNumber, 
            s.ScreeningDate, s.ScreeningTime, s.Price, p.PayTime
            FROM Tickets t
            JOIN Customers c ON t.CustomerID = c.CustomerID
            JOIN Screenings s ON t.ScreeningID = s.ScreeningID
            JOIN Seats se ON t.SeatID = se.SeatID
            JOIN Movies m ON s.MovieID = m.MovieID
            JOIN Cinemarooms r ON s.RoomID = r.RoomID
            JOIN Payments p ON t.TicketID = p.TicketID
            WHERE {}
            """
            if user_input.isdigit():
                condition = "t.TicketID = %s OR c.PhoneNumber = %s"
            
            final_query = query.format(condition)
            mycursor.execute(final_query, (user_input, user_input))
            results = mycursor.fetchall()
            print(results)
            self.display_results(results)
        
        except Error as e:
            print(f"Database error: {e}")
            return []
        except Exception as e:
            print(f"Error: {e}")
            self.display_results([])

        if not results:
            print("No tickets found for this phone number.")
            self.display_results([])

        
    def display_results(self, results):
        self.clear_rows()
        
        if not results:
            # Show "No results found" message
            no_result_lbl = tk.Label(self.inner_frame, text="No tickets found", 
                                   font=('Arial', 12), bg='white', fg='gray')
            no_result_lbl.grid(row=0, column=0, columnspan=11, pady=20)
            self.rows.append([no_result_lbl])
            return
        
        for i, row in enumerate(results):
            widgets = []
            ticket_id, customer_name, phone_number, movie, room, seat_num, date, time, price, pay_time = row
            
            # Check if action should be available
            show_action = self.check_action_conditions(row)
            values = [ticket_id, customer_name, phone_number, movie, room, date, seat_num, time, price, pay_time, 'Cancel' if show_action else '']

            for j, val in enumerate(values):
                lbl = tk.Label(self.inner_frame, text=val, font=('Arial', 10), bg='white', 
                             relief='solid', borderwidth=1, width=17)
                lbl.grid(row=i, column=j, sticky='nsew')  # Fixed: use self.inner_frame

                # Make Cancel button clickable
                if j == len(values)-1 and val == 'Cancel':
                    lbl.bind("<Button-1>", lambda e, tid=ticket_id: self.handle_action_click(tid))
                    lbl.config(fg='red', cursor='hand2')

                widgets.append(lbl)
            self.rows.append(widgets)
        
        # Update canvas scroll region after adding content
        self.after(10, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def check_action_conditions(self, ticket_data):
        try:
            ticket_date = datetime.strptime(str(ticket_data[6]), '%Y-%m-%d').date()
            today = datetime.now().date()
            return ticket_date >= today
        except (ValueError, IndexError) as e:
            print(f"Date parsing error: {e}")
            return False

    def handle_action_click(self, ticket_id):
        # TODO
        result = tk.messagebox.askyesno("Confirm Cancellation", 
                                      f"Are you sure you want to cancel ticket {ticket_id}?")
        if result:
            try:
                mycursor = self.main.mydb.cursor()
                delete_payment = "DELETE FROM Payments WHERE TicketID = %s"
                mycursor.execute(delete_payment, (ticket_id,))
                
                delete_ticket = "DELETE FROM Tickets WHERE TicketID = %s"
                mycursor.execute(delete_ticket, (ticket_id,))

                self.main.mydb.commit()
    
                if mycursor.rowcount > 0:
                    messagebox.showinfo("Success", f"Ticket {ticket_id} successfully cancelled.")
                else:
                    messagebox.showwarning("Warning", f"Ticket {ticket_id} was not found or already deleted.")
    
                self.search_ticket()  # Refresh the results
    
            except Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")
                
class Movie(tk.Toplevel):
    def __init__(self, main, username):
        super().__init__(main)
        self.title("Movie Selection")
        self.geometry("1000x700")
        self.configure(bg="white")
        self.main = main
        self.username = username
        self.movie_image_map = {}
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.movie_ui()

    def on_close(self):
        if self.main.mydb.is_connected():
            self.main.mydb.close()
        self.destroy()
        self.main.destroy()

    def back1(self):
        self.destroy()
        self.main.deiconify()

    def movie_ui(self):
        tk.Button(self, text="Logout", font=10, width=7, command=self.back1).grid(row=0, column=0, sticky="nw", padx=20, pady=20)

        titles = ["John Wick", "Edge of Tomorrow", "Interstellar", "Coco", "Parasite", "The Revenant"]
        images = [
            os.path.join(base_dir, "Images", "Johnwick.jpg"),
            os.path.join(base_dir, "Images", "EdgeOfTomorrow.jpg"),
            os.path.join(base_dir, "Images", "Interstellar.jpg"),
            os.path.join(base_dir, "Images", "Coco.jpg"),
            os.path.join(base_dir, "Images", "Parasite.jpg"),
            os.path.join(base_dir, "Images", "TheRevenant.jpg")
        ]

        self.movie_image_map = dict(zip(titles, images))

        grid_frame = tk.Frame(self, bg="white")
        grid_frame.place(relx=0.5, rely=0.55, anchor="center")

        for i, (title, img_path) in enumerate(zip(titles, images)):
            try:
                img = Image.open(img_path).resize((180, 230))
                img = ImageTk.PhotoImage(img)
            except:
                img = None

            btn = tk.Button(grid_frame, image=img, width=180, height=230,
                            command=lambda t=title: self.show_timeslots(t), bg="white", relief="solid", borderwidth=1)
            btn.image = img
            btn.grid(row=(i // 3) * 2, column=i % 3, padx=20, pady=10)

            tk.Label(grid_frame, text=title, bg="white", font=("Helvetica", 12)).grid(row=(i // 3) * 2 + 1, column=i % 3, pady=10)

    def show_timeslots(self, movie_title):
        if hasattr(self, 'timeslot_window') and self.timeslot_window.winfo_exists():
            self.timeslot_window.destroy()

        self.timeslot_window = tk.Toplevel(self)
        self.timeslot_window.title(f"Select Timeslot - {movie_title}")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_width = int(screen_width * 2 / 3)
        win_height = int(screen_height * 2 / 3)
        x_pos = int((screen_width - win_width) / 2)
        y_pos = int((screen_height - win_height) / 2)
        self.timeslot_window.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")
        self.timeslot_window.configure(bg="white")

        tk.Button(self.timeslot_window, text="BACK", command=self.timeslot_window.destroy).place(x=15, y=15)

        try:
            img_path = self.movie_image_map[movie_title]
            img = Image.open(img_path).resize((200, 280))
            poster_img = ImageTk.PhotoImage(img)
            poster = tk.Label(self.timeslot_window, image=poster_img, relief="solid", borderwidth=1)
            poster.image = poster_img
            poster.place(x=40, y=80)
        except:
            poster = tk.Label(self.timeslot_window, text="No\nImage", width=20, height=10, bg="lightgray", relief="solid")
            poster.place(x=40, y=80)

        tk.Label(self.timeslot_window, text=f"Movie schedule for '{movie_title}'", font=("Helvetica", 18, "bold"), bg="white").place(x=280, y=90)

        table_frame = tk.Frame(self.timeslot_window, bg="white")
        table_frame.place(x=270, y=150, width=win_width - 320, height=win_height - 230)

        columns = ("Date", "Time", "Format", "Room")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Helvetica", 13, "bold"))
        style.configure("Treeview", font=("Helvetica", 12), rowheight=36)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


        cursor = self.main.mydb.cursor()

        query = """
            SELECT s.ScreeningDate, s.ScreeningTime, s.MovieFormat, r.RoomName
            FROM Screenings s
            JOIN Movies m ON s.MovieID = m.MovieID
            JOIN CinemaRooms r ON s.RoomID = r.RoomID
            WHERE m.MovieTitle = %s AND s.ScreeningDate >= NOW()
            ORDER BY s.ScreeningDate, s.ScreeningTime
        """
        cursor.execute(query, (movie_title,))
        results = cursor.fetchall()

        for row in results:
            screening_date = row[0].strftime("%Y-%m-%d")
            screening_time = f"{row[1].seconds // 3600:02}:{(row[1].seconds // 60) % 60:02}"
            tree.insert("", "end", values=(screening_date, screening_time, row[2], row[3]))

        cursor.close()

        tk.Button(
            self.timeslot_window,
            text="SELECT",
            font=("Helvetica", 12),
            width=14,
            command=lambda: self.open_seat_booking(tree, movie_title)
        ).place(relx=0.5, rely=0.92, anchor="center")

    def open_seat_booking(self, tree, movie_title):
        selected_item = tree.focus()
        if not selected_item:
            messagebox.showwarning("No selection", "Please select a timeslot.")
            return

        values = tree.item(selected_item, 'values')
        screening_date, screening_time, movie_format, room_name = values

        # Truy vấn RoomID từ room_name
        query = """
                SELECT s.ScreeningID, s.Price, r.RoomID
                FROM Screenings s
                JOIN CinemaRooms r ON s.RoomID = r.RoomID
                JOIN Movies m ON s.MovieID = m.MovieID
                WHERE m.MovieTitle = %s AND s.ScreeningDate = %s AND s.ScreeningTime = %s AND r.RoomName = %s
            """
        cursor = self.main.mydb.cursor()
        cursor.execute(query, (movie_title, screening_date, screening_time, room_name))
        result = cursor.fetchone()
        cursor.close()
        if not result:
            messagebox.showerror("Error", "Screening not found.")
            return

        screening_id, price, room_id = result

        # Gọi GUI SeatBooking và truyền dữ liệu
        self.withdraw()
        self.timeslot_window.destroy()
        SeatBooking(self, self.main.mydb,screening_id, room_name, price)
    
class SeatBooking(tk.Toplevel):
    def __init__(self, parent, db_connection, screening_id, room_name, seat_price):
        #root
        super().__init__(parent)
        self.parent = parent
        self.db = db_connection
        self.screening_id = screening_id
        self.room_name = room_name
        self.seat_price = seat_price
        self.total_price = 0
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.geometry("1200x700")
        self.title("Seat booking")
        self.resizable(False, False)
        
        # Initialize data structures
        self.selected_seats = {}
        self.booked_seats = set()  #Query booked seat
        
        self.query_booked_seats()
        self.main_interface()
        
    def on_close(self):
        if self.db.is_connected():
            self.db.close()
        self.destroy()
        self.parent.destroy()
    def query_booked_seats(self):
        cursor = self.db.cursor()
        query = """
            SELECT SeatNumber FROM Seats se
            JOIN Screenings s ON se.RoomID = s.RoomID
            WHERE ScreeningID = %s AND SeatStatus = 'Booked'
        """
        cursor.execute(query, (self.screening_id,))
        results = cursor.fetchall()
        self.booked_seats = set(row[0] for row in results)
        cursor.close()

    def log_out_2(self):
        self.destroy()
        self.parent.deiconify()

    def main_interface(self):
        # Frames
        top_frame = tk.Frame(self, bd=3, relief="solid", bg="light grey")
        top_frame.place(x=700,y=30, anchor="n")
        
        bottom_frame = tk.Frame(self)
        bottom_frame.place(x=300,y=600)
        
        seat_frame = tk.Frame(self)
        seat_frame.place(x=700,y=350, anchor="center")
        
        tleft_frame = tk.Frame(self, bd = 1, relief= "solid")
        tleft_frame.place(x=100, y = 150)
        
        left_frame = tk.Frame(self)
        left_frame.place(x=100,y=350, anchor="w")
        
        #Main interface

        back_button = tk.Button(self, text="BACK", font=("Arial", 10), width=7, height=1, command=self.log_out_2)
        back_button.place(x=30, y=30)
        
        # Continue button (initially disabled)
        self.continue_button = tk.Button(self, text="Payment", 
                                         font=("bold,14"), 
                                         bg="#4CAF50", fg="white",
                                         width=10, height=1,
                                         state="disabled",
                                         command=self.go_to_payment)
        self.continue_button.place(x=1050,y=350)
        ###Screen label
        screen_label = tk.Label(top_frame, text = "Screen", width=30, font = ("Bold",30), justify = "center", bg = "light grey")
        screen_label.pack(padx=10, pady=10, anchor=tk.CENTER)
        
        ###CinemaRoom label
        room_label = tk.Label(tleft_frame, text = f"{self.room_name}", width = 20, font = ("Bold"), justify = "left")
        room_label.pack(pady=(10,10))
        
        ###Legends
        available_seat = tk.Frame(left_frame, width=40, height=40, bg= "white", relief=tk.RIDGE, bd=1)
        available_seat.grid(row = 0, column=0)
        
        available_label = tk.Label(left_frame, text = "Available seat", font = 10)
        available_label.grid(row= 0, column=1, padx=10, pady=10, sticky='w')
        
        selected_seat = tk.Frame(left_frame, width=40, height=40, bg= "blue", relief=tk.RIDGE, bd=1)
        selected_seat.grid(row = 1, column=0)
        
        selected_label = tk.Label(left_frame, text = "Selected seat", font = 10)
        selected_label.grid(row= 1, column=1, padx=10, pady=10, sticky='w')
        
        booked_seat = tk.Frame(left_frame, width=40, height=40, bg= "red", relief=tk.RIDGE, bd=1)
        booked_seat.grid(row = 2, column=0)
        
        booked_label = tk.Label(left_frame, text = "Booked seat", font = 10)
        booked_label.grid(row= 2, column=1, padx=10, pady=10, sticky='w')
        
        ###Bottom text
        self.total_seat = tk.Label(bottom_frame, text = "Total selected seats: 0", font=("Bold",20))
        self.total_seat.grid(row=0, column=0)
        
        self.est_price = tk.Label(bottom_frame, text = "Est. Price: 0 VND", font=("Bold", 20))
        self.est_price.grid(row=0, column=1, padx=150)
        
        #Seat layout
        self.seat_buttons = {}
        for row in range(8):
            for col in range(8):
                seat_number = f"{chr(65+row)}{col+1}"  # A1, A2, ...
                
                # Determine initial color
                if seat_number in self.booked_seats:
                    bg_color = "red"
                    fg_color= "white"
                    state = "disabled"
                else:
                    bg_color = "white"
                    fg_color = "black"
                    state = "normal"
                  
                seat_button = tk.Button(seat_frame, width=4, height=2, text=f"{seat_number}", relief=tk.RIDGE,bd=1,
                    fg=fg_color, state=state, bg = bg_color, command=lambda s=seat_number: self.toggle_seat(s) #seat selection command
                )
                seat_button.grid(row=row+1, column=col+1, padx=15, pady=5)
                self.seat_buttons[seat_number] = seat_button
                
    def toggle_seat(self,seat_number):
        # Check if seat is already booked (red)
        if self.seat_buttons[seat_number].cget("bg") == "red":
            return  # Can't select already booked seats
        
        # Check if the seat is already selected
        if seat_number in self.selected_seats:
        # Deselect the seat
            self.seat_buttons[seat_number].config(bg="white", fg = "black")
            del self.selected_seats[seat_number]
        else:

            self.seat_buttons[seat_number].config(bg="blue", fg = "white")
            self.selected_seats[seat_number] = True
        # Update total selected seats and price
        self.update_totals()
        
    def update_totals(self):
       total_selected = len(self.selected_seats)
       self.total_price = total_selected * self.seat_price
       
       self.total_seat.config(text=f"Total selected seats: {total_selected}")
       self.est_price.config(text=f"Est. Price: {self.total_price} VND")
        
       if total_selected > 0:
           self.continue_button.config(state="normal")
       else:
           self.continue_button.config(state="disabled")
           
    def go_to_payment(self):
        self.withdraw()
        CustomerFormApp(self, self.db, self.screening_id, self.selected_seats, self.total_price)

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
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()
    
    def back4(self):
        self.destroy()
        self.parent.deiconify()
    def on_close(self):
        if self.parent.db.is_connected():
            self.parent.db.close()
        self.destroy()
        self.parent.destroy()  

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
            #Query customer
            cursor.execute("SELECT CustomerID FROM Customers WHERE PhoneNumber = %s", (phone,))
            customer_id_result = cursor.fetchone()
            if customer_id_result:
                customer_id = customer_id_result[0]
            else:
                cursor.execute(
                    "INSERT INTO Customers (CustomerName, DOB, PhoneNumber) VALUES (%s, %s, %s)",
                    (customer_name, dob, phone)
                )
                cursor.execute("SELECT LAST_INSERT_ID()")
                customer_id = cursor.fetchone()[0]
            #Query room
            cursor.execute("SELECT RoomID FROM Screenings WHERE ScreeningID = %s", (screening_id,))
            room_id_result = cursor.fetchone()
            if not room_id_result:
                messagebox.showerror("Error", "Screening does not exist")
                return
            room_id = room_id_result[0]  
              
            for seat in selected_seats.keys():
                try:
                    cursor.execute("SELECT SeatID FROM Seats WHERE RoomID = %s AND SeatNumber = %s", (room_id, seat))
                    seat_id_result = cursor.fetchone()
                    seat_id = seat_id_result[0]    
                    
                    cursor.execute("INSERT INTO Tickets(CustomerID,ScreeningID,SeatID) VALUES(%s,%s,%s)",
                    (customer_id,screening_id,seat_id))
    
                    cursor.execute("""
                       SELECT TicketID FROM Tickets 
                       WHERE CustomerID = %s AND ScreeningID = %s AND SeatID = %s
                       ORDER BY TicketID DESC LIMIT 1
                   """, (customer_id, screening_id, seat_id))
                    ticket_id = cursor.fetchone()[0]
                    ticket_ids.append(ticket_id)
                except mysql.connector.Error as seat_err:
                    messagebox.showerror("Database Error", f"Error: {seat_err}")
                    continue
                    # Insert payments for each ticket
            for ticket_id in ticket_ids:
                cursor.execute("""
                    INSERT INTO Payments (CustomerID, ScreeningID, TicketID, Amount, PayTime)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (customer_id, screening_id, ticket_id, amount_due/len(ticket_ids)))
            self.mydb.commit()
            messagebox.showinfo("Success", f"{len(ticket_ids)} ticket(s) booked successfully!")
                
        except mysql.connector.Error as err:
            if cursor:
                messagebox.showerror("Database Error", f"Error: {err}")
        finally:
            if cursor:
                cursor.close()

    def create_widgets(self):
        #Confirm button
        Button(self, text="Confirm", font=("Arial", 10), width=15, command=self.confirm_form).place(x=330, y=420)
        Button(self, text="BACK", font=("Arial", 10), width=7, command= self.back4).place(x=10, y=10)
        
        #Customer name
        Label(self, text="Customer Name:").place(x=80, y=100)
        vcmd_name = (self.register(self.validate_name_input), '%P')
        self.customer_name_entry = tk.Entry(self, width=40, validate='key', validatecommand = vcmd_name)
        self.customer_name_entry.place(x=250, y=100)
        
        #DOB
        Label(self, text="DOB - optional:").place(x=80, y=150)
        self.day_entry = tk.Entry(self, width=3, validate='key', validatecommand=(self.register(self.validate_day_input), '%P'))
        self.day_entry.place(x=250, y=150)
        Label(self, text="/").place(x=275, y=150)
        self.month_entry = tk.Entry(self, width=3, validate='key', validatecommand=(self.register(self.validate_month_input), '%P'))
        self.month_entry.place(x=285, y=150)
        Label(self, text="/").place(x=310, y=150)
        self.year_entry = tk.Entry(self, width=5, validate='key', validatecommand=(self.register(self.validate_year_input), '%P'))
        self.year_entry.place(x=320, y=150)
        
        #Phone number
        Label(self, text="Phone Number:").place(x=80, y=200)
        vcmd_phone = (self.register(self.validate_phone_input), '%P')
        self.phone_entry = tk.Entry(self, width=40, validate='key', validatecommand = vcmd_phone)
        self.phone_entry.place(x=250, y=200)
        

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
    
       
class Admin(tb.Window):
    def __init__(self, main):
        super().__init__(themename="litera")
        self.title("Liemora's Report")
        self.geometry("1600x900")
        self.resizable(False, False)
        self.configure(bg="white")
        self.main = main
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.sort_orders = {}
        self.sort_states = {}
        self.current_dataframe = None
        self.current_dataframe2 = None
        self.current_dataframe3 = None
        self.current_figure = None
        self.current_figure2 = None
        self.current_figure3 = None



        self.tab_control = tb.Notebook(self)
        self.tab_control.pack(expand=True, fill='both', padx=20, pady=20)
        self.tab1 = tb.Frame(self.tab_control)
        self.tab2 = tb.Frame(self.tab_control)
        self.tab3 = tb.Frame(self.tab_control)

        self.tab_control.add(self.tab1, text='📊 Sales Overview')
        self.tab_control.add(self.tab2, text='📈 Performance Report')
        self.tab_control.add(self.tab3, text='👥 Customer Insight')

        self.tab_control.bind("<<NotebookTabChanged>>", self.on_tab_changed)


        for tab in (self.tab1, self.tab2, self.tab3):
            main_frame = tb.Frame(tab)
            main_frame.pack(fill="both", expand=True)

            self.left_frame = tb.Frame(main_frame, width=180)
            self.left_frame.pack(side="left", fill="y")

            right_frame = tb.Frame(main_frame)
            right_frame.pack(side="right", fill="both", expand=True)

            #Button
            if tab == self.tab1:
                self.graph_frame = tb.Frame(right_frame)
                self.graph_frame.pack(fill="both", expand=True)
                self.buttons_frame = tb.Frame(right_frame)
                self.buttons_frame.pack(fill="x", pady=10)

                #Left buttons
                tb.Button(self.left_frame, text="Logout",width=20, command=self.logout).pack(pady=3,padx=5,side="bottom",ipady=10)
                tb.Button(self.left_frame, text="Export as Excel\n(With PNG if available)", width=20, command=self.excel_export).pack(pady=3,padx=5,side="bottom",ipady=10)
                tb.Button(self.left_frame, width=20,  text="Total Revenue",command=self.display_total_revenue).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame,width=20, text="Revenue Trends", command=self.display_revenue_sales_chart).pack(pady=3,padx=5,ipady=10)
                tb.Button(self.left_frame, text="Total Ticket Sold", width=20,  command=self.display_ticket).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Tickets Sold Trend", width=20, command=self.display_ticket_chart).pack(pady=3, padx=5,ipady=10)

                #Revenue and ticket trend buttons
                self.all_time_btn = tb.Button(self.buttons_frame, text="All time", width=20,
                                              command=lambda: self.update_chart_by_range("all"))
                self.last_year_btn = tb.Button(self.buttons_frame, text="Last year", width=20,
                                               command=lambda: self.update_chart_by_range("year"))
                self.last_6_months_btn = tb.Button(self.buttons_frame, text="Last 6 months", width=20,
                                                   command=lambda: self.update_chart_by_range("6m"))
                self.last_30_days_btn = tb.Button(self.buttons_frame, text="Last 30 days", width=20,
                                                  command=lambda: self.update_chart_by_range("30"))

                #Revenue
                self.revenue_daily_btn = tb.Button(self.buttons_frame, text="Daily",width=20,command=self.revenue_daily)
                self.revenue_monthly_btn = tb.Button(self.buttons_frame, text="Monthly", width=20, command=self.revenue_monthly)
                self.revenue_quarterly_btn = tb.Button(self.buttons_frame, text="Quarterly", width=20, command=self.revenue_quarterly)
                self.revenue_yearly_btn = tb.Button(self.buttons_frame, text="Yearly", width=20, command=self.revenue_yearly)

                #Ticket
                self.ticket_daily_btn = tb.Button(self.buttons_frame, text="Daily", width=20, command=self.ticket_daily)
                self.ticket_monthly_btn = tb.Button(self.buttons_frame, text="Monthly", width=20,command=self.ticket_monthly)
                self.ticket_quarterly_btn = tb.Button(self.buttons_frame, text="Quarterly", width=20, command=self.ticket_quarterly)
                self.ticket_yearly_btn = tb.Button(self.buttons_frame, text="Yearly", width=20, command=self.ticket_yearly)

            elif tab == self.tab2:
                self.graph_frame2 = tb.Frame(right_frame)
                self.graph_frame2.pack(fill="both", expand=True)
                self.buttons_frame2 = tb.Frame(right_frame)
                self.buttons_frame2.pack(fill="x", pady=10)

                tb.Button(self.left_frame, text="Logout",width=20,command=self.logout).pack(pady=3, padx=5,ipady=10,side="bottom",)
                tb.Button(self.left_frame, text="Movie Performance", width=20, command=self.display_movie).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Occupancy Rate", width=20,  command=self.display_occupation).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Screening Time", width=20, command=self.display_screening_time).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Weekday Performance", width=20, command=self.day_performance).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Movie Format", width=20,
                          command=self.format_performance).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Export as Excel\n(With PNG if available)", width=20,
                                              command=self.excel_export2).pack(pady=3, padx=5,ipady=10, side="bottom")

                #Movies
                self.last_14days = tb.Button(self.buttons_frame2, text="Last 14 days", width=20,command=self.display_movie14)
                self.last_30days = tb.Button(self.buttons_frame2, text="Last 30 days", width=20, command=self.display_movie30)
                self.last_60days = tb.Button(self.buttons_frame2, text="Last 60 days", width=20, command=self.display_movie60)

                #Occupancy
                self.Occupation_table = tb.Button(self.buttons_frame2, text="Table", width=20,
                                             command=self.display_occupation_table)
                self.Occupation_graph = tb.Button(self.buttons_frame2, text="Graph", width=20,
                                                  command=self.display_occupation_graph)

                #Screening
                self.screening30 = tb.Button(self.buttons_frame2, text="Last 30 days", width=20,
                                             command=self.display_screening30)
                self.screening90 = tb.Button(self.buttons_frame2, text="Last 90 days", width=20,
                                           command=self.display_screening90)
                self.screening = tb.Button(self.buttons_frame2, text="All time", width=20,
                                           command=self.display_screening)
                #Day Performance
                self.day_30 = tb.Button(self.buttons_frame2, text="Last 30 days", width=20,
                                             command=self.display_day30)
                self.day_90 = tb.Button(self.buttons_frame2, text="Last 90 days", width=20,
                                             command=self.display_day90)
                self.day_all = tb.Button(self.buttons_frame2, text="All time", width=20,
                                             command=self.display_day_all)
                #Format Performance
                self.format_30_bt = tb.Button(self.buttons_frame2, text="Last 30 days", width=20,
                                         command=self.format_30)
                self.format_90_bt = tb.Button(self.buttons_frame2, text="Last 90 days", width=20,
                                         command=self.format_90)
                self.format_year_bt = tb.Button(self.buttons_frame2, text="Last year", width=20,
                                         command=self.format_year)
                self.format_all_bt = tb.Button(self.buttons_frame2, text="All time", width=20,
                                         command=self.format_all)

            elif tab == self.tab3:
                self.graph_frame3 = tb.Frame(right_frame)
                self.graph_frame3.pack(fill="both", expand=True)
                self.buttons_frame3 = tb.Frame(right_frame)
                self.buttons_frame3.pack(fill="x", pady=10)

                tb.Button(self.left_frame, text="Logout",width=20, command=self.logout).pack(pady=3, padx=5,ipady=10,side="bottom")
                tb.Button(self.left_frame, text="Age Distribution", width=20, command=self.display_age).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Genre By Age", width=20, command=self.display_age_genre).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Time Preference By Age", width=20,command=self.display_time_age).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Format Preference By Age", width=20,command=self.display_format_age).pack(pady=3, padx=5,ipady=10)
                tb.Button(self.left_frame, text="Export as Excel\n(With PNG if available)", width=20,
                                               command=self.excel_export3).pack(pady=3, padx=5,ipady=10, side="bottom")

                #Age
                self.age_90 = tb.Button(self.buttons_frame3, text="Last 90 days", width=20,
                                        command=self.age90)
                self.age_year = tb.Button(self.buttons_frame3, text="Last year", width=20,
                                        command=self.ageyear)
                self.age_all = tb.Button(self.buttons_frame3, text="All time", width=20,
                                         command=self.ageall)
                #Age-Genre
                self.genre_17 = tb.Button(self.buttons_frame3, text="Age 12-17", width=20,
                                        command=self.genre17)
                self.genre_25 = tb.Button(self.buttons_frame3, text="Age 18-25", width=20,
                                        command=self.genre25)
                self.genre_40 = tb.Button(self.buttons_frame3, text="Age 26-40", width=20,
                                        command=self.genre40)
                self.genre_60 = tb.Button(self.buttons_frame3, text="Age 41-60", width=20,
                                          command=self.genre60)
                self.genre_above = tb.Button(self.buttons_frame3, text="Above 60+", width=20,
                                          command=self.genre_above_60)
                self.genre_screening = tb.Button(self.buttons_frame3, text="Genre Screening Count", width=20,
                                             command=self.genre_screening_1)

                #Age-ScreeningTime
                self.age_time_30_bt = tb.Button(self.buttons_frame3, text="Last 30 days", width=20,
                                          command=self.age_time_30)
                self.age_time_90_bt = tb.Button(self.buttons_frame3, text="Last 90 days", width=20,
                                          command=self.age_time_90)
                self.age_time_year_bt = tb.Button(self.buttons_frame3, text="Last year", width=20,
                                          command=self.age_time_year)
                self.age_time_all_bt = tb.Button(self.buttons_frame3, text="All time", width=20,
                                          command=self.age_time_all)
                #Age-Format
                self.age_format_30_bt = tb.Button(self.buttons_frame3, text="Last 30 days", width=20,
                                                 command=self.age_format_30)
                self.age_format_90_bt = tb.Button(self.buttons_frame3, text="Last 90 days", width=20,
                                                 command=self.age_format_90)
                self.age_format_year_bt = tb.Button(self.buttons_frame3, text="Last year", width=20,
                                                 command=self.age_format_year)
                self.age_format_all_bt = tb.Button(self.buttons_frame3, text="All time", width=20,
                                                 command=self.age_format_all)

    def on_tab_changed(self, event):
        selected_tab = self.tab_control.select()
        tab_index = self.tab_control.index(selected_tab)

        if tab_index == 0:
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            self.graph_frame.update_idletasks()
        elif tab_index == 1:
            for widget in self.graph_frame2.winfo_children():
                widget.destroy()
            self.graph_frame2.update_idletasks()
        elif tab_index == 2:
            for widget in self.graph_frame3.winfo_children():
                widget.destroy()
            self.graph_frame3.update_idletasks()

        self.left_frame.update()
        self.left_frame.update_idletasks()
        self.tab_control.update()
        self.update_idletasks()
    def excel_export(self):
        if self.current_dataframe is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save as Excel"
        )
        if file_path:
            try:

                self.current_dataframe.to_excel(file_path, index=False)


                if hasattr(self, 'current_figure') and self.current_figure:
                    image_path = os.path.splitext(file_path)[0] + ".png"
                    self.current_figure.savefig(image_path, dpi=300)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export:\n{e}")
    def excel_export2(self):
        if self.current_dataframe2 is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save as Excel"
        )
        if file_path:
            try:

                self.current_dataframe2.to_excel(file_path, index=False)

                if hasattr(self, 'current_figure') and self.current_figure2:
                    image_path = os.path.splitext(file_path)[0] + ".png"
                    self.current_figure2.savefig(image_path, dpi=300)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export:\n{e}")
    def excel_export3(self):
        if self.current_dataframe3 is None:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save as Excel"
        )
        if file_path:
            try:

                self.current_dataframe3.to_excel(file_path, index=False)

                if hasattr(self, 'current_figure') and self.current_figure3:
                    image_path = os.path.splitext(file_path)[0] + ".png"
                    self.current_figure3.savefig(image_path, dpi=300)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export:\n{e}")
    #DEF TAB1
    def on_close(self):
        if self.main.mydb and self.main.mydb.is_connected():
            self.main.mydb.close()
        self.destroy()
        self.main.destroy()
    def logout(self):
        self.main.mydb.close()
        self.destroy()
        self.main.account_entry.delete(0, tk.END)
        self.main.password_entry.delete(0, tk.END)
        self.main.deiconify()
    def hide_time_range_totalrevenue(self):
        self.revenue_daily_btn.pack_forget()
        self.revenue_monthly_btn.pack_forget()
        self.revenue_quarterly_btn.pack_forget()
        self.revenue_yearly_btn.pack_forget()
    def show_time_range_totalrevenue(self):
        self.revenue_daily_btn.pack(side="right", padx=10)
        self.revenue_monthly_btn.pack(side="right", padx=10)
        self.revenue_quarterly_btn.pack(side="right", padx=10)
        self.revenue_yearly_btn.pack(side="right", padx=10)
    def hide_time_range_buttons(self):
        self.all_time_btn.pack_forget()
        self.last_year_btn.pack_forget()
        self.last_6_months_btn.pack_forget()
        self.last_30_days_btn.pack_forget()
    def show_time_range_button(self):
        self.last_30_days_btn.pack(side="right", padx=10)
        self.last_6_months_btn.pack(side="right", padx=10)
        self.last_year_btn.pack(side="right", padx=10)
        self.all_time_btn.pack(side="right", padx=10)
    def show_time_range_ticket(self):
        self.ticket_daily_btn.pack(side="right", padx=10)
        self.ticket_monthly_btn.pack(side="right", padx=10)
        self.ticket_quarterly_btn.pack(side="right", padx=10)
        self.ticket_yearly_btn.pack(side="right", padx=10)
    def hide_time_range_ticket(self):
        self.ticket_daily_btn.pack_forget()
        self.ticket_monthly_btn.pack_forget()
        self.ticket_quarterly_btn.pack_forget()
        self.ticket_yearly_btn.pack_forget()
    def update_chart_by_range(self, range_type):
        if self.chart_mode == "revenue":
            if range_type == "30":
                self.display_30_days_revenue()
            elif range_type == "6m":
                self.display_6_months_revenue()
            elif range_type == "year":
                self.display_year_revenue()
            elif range_type == "all":
                self.display_alltime_revenue()
        elif self.chart_mode == "ticket":
            if range_type == "30":
                self.display_ticket_30days()
            elif range_type == "6m":
                self.display_ticket_6months()
            elif range_type == "year":
                self.display_ticket_year()
            elif range_type == "all":
                self.display_ticket_alltime()
    #Revenue trend
    def display_revenue_sales_chart(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()

        query = """
                SELECT 
                    Date, 
                    TotalRevenue 
                FROM 
                    revenue_30days
                ORDER BY 
                    Date;
            """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for chart.")
            df['Date'] = pd.to_datetime(df['Date'])

            fig = Figure(figsize=(11,6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)
            ax.plot(df['Date'], df['TotalRevenue'], marker='o', linestyle='-', color='green')
            ax.set_title("Revenue Over Last 30 Days")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Revenue")
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
        except Exception as e:
            print(f"Error generating chart: {e}")
        self.hide_time_range_ticket()
        self.hide_time_range_totalrevenue()
        self.show_time_range_button()
        self.chart_mode = "revenue"
        self.update_chart_by_range("30")
    def display_30_days_revenue(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        query = """
                SELECT 
                    Date, 
                    TotalRevenue 
                FROM 
                    revenue_30days
                ORDER BY 
                    Date;
            """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for chart.")
            df['Date'] = pd.to_datetime(df['Date'])

            fig = Figure(figsize=(11, 6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)
            ax.plot(df['Date'], df['TotalRevenue'], marker='o', linestyle='-', color='green')
            ax.set_title("Revenue Over Last 30 Days")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Revenue")
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()


            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating chart: {e}")
    def display_6_months_revenue(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        query = """
            SELECT 
                Date, 
                TotalRevenue 
            FROM 
                revenue_6months
            ORDER BY 
                Date;
        """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for 6-month revenue.")
            df['Date'] = pd.to_datetime(df['Date'])

            fig = Figure(figsize=(11, 6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)
            ax.plot(df['Date'], df['TotalRevenue'], marker='o', linestyle='-', color='green')
            ax.set_title("Revenue Over Last 6 Months")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Revenue")
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating 6-month chart: {e}")
    def display_year_revenue(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        query = """
            SELECT 
                Date, 
                TotalRevenue 
            FROM 
                revenue_year
            ORDER BY 
                Date;
        """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for yearly revenue.")
            df['Date'] = pd.to_datetime(df['Date'])

            fig = Figure(figsize=(11, 6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)
            ax.plot(df['Date'], df['TotalRevenue'], marker='o', linestyle='-', color='green')
            ax.set_title("Revenue Over Last Year")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Revenue")
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()


            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating yearly chart: {e}")
    def display_alltime_revenue(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        query = """
            SELECT 
                Date, 
                TotalRevenue 
            FROM 
                revenue_alltime
            ORDER BY 
                Date;
        """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for all-time revenue.")

            fig = Figure(figsize=(11, 6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)


            ax.bar(df['Date'], df['TotalRevenue'], color='green')

            ax.set_title("All-Time Revenue (Quarterly)")
            ax.set_xlabel("Quarter")
            ax.set_ylabel("Total Revenue")
            ax.ticklabel_format(style='plain', axis='y')
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            fig.autofmt_xdate()
            fig.tight_layout()



            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating all-time chart: {e}")
    #ticket trend
    def display_ticket_chart(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        query = """
            SELECT 
                Date, 
                TotalTicketsSold 
            FROM 
                ticket_30days
            ORDER BY 
                Date;
        """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for ticket sales.")

            fig = Figure(figsize=(11, 6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)


            ax.plot(df['Date'], df['TotalTicketsSold'], marker='o', linestyle='-', color='blue')
            ax.set_title("Tickets Sold Over Last 30 Days")
            ax.set_xlabel("Date")
            ax.set_ylabel("Tickets Sold")
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load ticket sales chart.\n{str(e)}")

        self.hide_time_range_ticket()
        self.hide_time_range_totalrevenue()
        self.show_time_range_button()
        self.chart_mode = "ticket"
        self.update_chart_by_range("30")
    def display_ticket_30days(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        query = """
                    SELECT 
                        Date, 
                        TotalTicketsSold 
                    FROM 
                        ticket_30days
                    ORDER BY 
                        Date;
                """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for ticket sales.")

            fig = Figure(figsize=(11, 6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)


            ax.plot(df['Date'], df['TotalTicketsSold'], marker='o', linestyle='-', color='blue')
            ax.set_title("Tickets Sold Over Last 30 Days")
            ax.set_xlabel("Date")
            ax.set_ylabel("Tickets Sold")
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()


            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load ticket sales chart.\n{str(e)}")
    def display_ticket_6months(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        query = """
                    SELECT 
                        Date, 
                        TotalTicketsSold 
                    FROM 
                        ticket_6months
                    ORDER BY 
                        Date;
                """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for ticket sales.")

            fig = Figure(figsize=(11, 6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)


            ax.plot(df['Date'], df['TotalTicketsSold'], marker='o', linestyle='-', color='blue')
            ax.set_title("Tickets Sold Over Last 6 Months")
            ax.set_xlabel("Date")
            ax.set_ylabel("Tickets Sold")
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()



            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load ticket sales chart.\n{str(e)}")
    def display_ticket_year(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        query = """
                            SELECT 
                                Date, 
                                TotalTicketsSold 
                            FROM 
                                ticket_year
                            ORDER BY 
                                Date;
                        """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for ticket sales.")

            fig = Figure(figsize=(11, 6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)


            ax.plot(df['Date'], df['TotalTicketsSold'], marker='o', linestyle='-', color='blue')
            ax.set_title("Tickets Sold Over Last Year")
            ax.set_xlabel("Date")
            ax.set_ylabel("Tickets Sold")
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()


            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load ticket sales chart.\n{str(e)}")
    def display_ticket_alltime(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()

        query = """
             SELECT 
                 Date, 
                 TotalTicketsSold 
             FROM 
                 ticket_alltime
             ORDER BY 
                 Date;
         """
        try:
            df = pd.read_sql(query, self.main.mydb)
            self.current_dataframe = df.copy()
            if df.empty:
                raise ValueError("No data found for all-time ticket sold.")

            fig = Figure(figsize=(11, 6), dpi=100)
            self.current_figure = fig
            ax = fig.add_subplot(111)


            ax.bar(df['Date'], df['TotalTicketsSold'], color='blue')

            ax.set_title("All-Time Ticket Sold (Quarterly)")
            ax.set_xlabel("Quarter")
            ax.set_ylabel("Total Ticket")
            ax.ticklabel_format(style='plain', axis='y')
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            fig.autofmt_xdate()
            fig.tight_layout()


            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating all-time chart: {e}")
    #Revenue
    def display_total_revenue(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = """
                        SELECT
                            DATE(PayTime) AS PayDate,
                            SUM(Amount) AS TotalRevenue
                        FROM Payments
                        GROUP BY PayDate
                        ORDER BY PayDate DESC;
                        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("YearMonth", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def sort_column(col, reverse):
            data_list = [(tree.set(k, col), k) for k in tree.get_children('')]
            if col == "TotalRevenue":
                data_list.sort(key=lambda t: int(t[0].replace(".", "").replace(" ₫", "")), reverse=reverse)
            else:
                data_list.sort(reverse=reverse)

            for index, (val, k) in enumerate(data_list):
                tree.move(k, '', index)
            tree.heading(col, command=lambda: sort_column(col, not reverse))
        tree.heading("YearMonth", text="Date", command=lambda: sort_column("YearMonth", False))
        tree.heading("TotalRevenue", text="Total Revenue", command=lambda: sort_column("TotalRevenue", False))
        for row in data:
            year_month, total_revenue = row
            formatted_revenue = "{:,.0f} ₫".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))

        self.hide_time_range_buttons()
        self.hide_time_range_ticket()
        self.show_time_range_totalrevenue()
    def revenue_daily(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        cursor = self.main.mydb.cursor()
        query = """
                SELECT
                    DATE(PayTime) AS PayDate,
                    SUM(Amount) AS TotalRevenue
                FROM Payments
                GROUP BY PayDate
                ORDER BY PayDate DESC;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("YearMonth", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.heading("YearMonth", text="Date")
        tree.heading("TotalRevenue", text="Total Revenue")
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in data:
            year_month, total_revenue = row
            formatted_revenue = "{:,.0f} ₫".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))
    def revenue_monthly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = """
                        SELECT
                           DATE_FORMAT(PayTime, '%Y-%m') AS YearMonth,
                           SUM(Amount) AS TotalRevenue
                        FROM Payments
                        GROUP BY YearMonth
                        ORDER BY YearMonth DESC;
                        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("YearMonth", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def sort_column(col, reverse):
            data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

            if col == "TotalRevenue":
                data_list.sort(key=lambda t: int(t[0].replace(".", "").replace(" ₫", "")), reverse=reverse)
            else:
                data_list.sort(reverse=reverse)

            for index, (val, k) in enumerate(data_list):
                tree.move(k, '', index)

            tree.heading(col, command=lambda: sort_column(col, not reverse))

        tree.heading("YearMonth", text="Date", command=lambda: sort_column("YearMonth", False))
        tree.heading("TotalRevenue", text="Total Revenue", command=lambda: sort_column("TotalRevenue", False))

        for row in data:
            year_month, total_revenue = row
            formatted_revenue = "{:,.0f} ₫".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))
    def revenue_quarterly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        cursor = self.main.mydb.cursor()
        query = """
                SELECT
                      CONCAT(Year, '-Q', Quarter) AS YearQuarter,
                      SUM(Total) AS TotalRevenue
                FROM (
                    SELECT 
                        YEAR(PayTime) AS Year,
                        QUARTER(PayTime) AS Quarter,
                        Amount AS Total
                    FROM Payments
                ) AS sub
                GROUP BY Year, Quarter
                ORDER BY Year DESC, Quarter DESC;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("YearMonth", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.heading("YearMonth", text="Date")
        tree.heading("TotalRevenue", text="Total Revenue")
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def sort_column(col, reverse):
            data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

            if col == "TotalRevenue":
                data_list.sort(key=lambda t: int(t[0].replace(".", "").replace(" ₫", "")), reverse=reverse)
            else:
                data_list.sort(reverse=reverse)

            for index, (val, k) in enumerate(data_list):
                tree.move(k, '', index)

            tree.heading(col, command=lambda: sort_column(col, not reverse))

        tree.heading("YearMonth", text="Date", command=lambda: sort_column("YearMonth", False))
        tree.heading("TotalRevenue", text="Total Revenue", command=lambda: sort_column("TotalRevenue", False))

        for row in data:
            year_month, total_revenue = row
            formatted_revenue = "{:,.0f} ₫".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))
    def revenue_yearly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        cursor = self.main.mydb.cursor()
        query = """
                SELECT
                  Year,
                  SUM(Total) AS TotalRevenue
                FROM (
                  SELECT 
                    YEAR(PayTime) AS Year,
                    Amount AS Total
                  FROM Payments
                ) AS sub
                GROUP BY Year
                ORDER BY Year desc;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("YearMonth", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.heading("YearMonth", text="Date")
        tree.heading("TotalRevenue", text="Total Revenue")
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def sort_column(col, reverse):
            data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

            if col == "TotalRevenue":
                data_list.sort(key=lambda t: int(t[0].replace(".", "").replace(" ₫", "")), reverse=reverse)
            else:
                data_list.sort(reverse=reverse)

            for index, (val, k) in enumerate(data_list):
                tree.move(k, '', index)

            tree.heading(col, command=lambda: sort_column(col, not reverse))

        tree.heading("YearMonth", text="Date", command=lambda: sort_column("YearMonth", False))
        tree.heading("TotalRevenue", text="Total Revenue", command=lambda: sort_column("TotalRevenue", False))

        for row in data:
            year_month, total_revenue = row
            formatted_revenue = "{:,.0f} ₫".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))
    #Ticket
    def display_ticket(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = """
                        SELECT
                          DATE(PayTime) AS SaleDate,
                          COUNT(TicketID) AS TotalTicketsSold
                        FROM Payments
                        GROUP BY DATE(PayTime)
                        ORDER BY SaleDate DESC;
                        """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("SaleDate", "TotalTicketsSold")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.column("SaleDate", width=150, anchor="center")
        tree.column("TotalTicketsSold", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)


        def sort_column(col, reverse):

            data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

            if col == "TotalTicketsSold":

                data_list.sort(key=lambda t: int(t[0].replace(".", "")), reverse=reverse)
            else:
                data_list.sort(key=lambda t: t[0], reverse=reverse)

            for index, (val, k) in enumerate(data_list):
                tree.move(k, '', index)

            tree.heading(col, command=lambda: sort_column(col, not reverse))


        tree.heading("SaleDate", text="Date", command=lambda: sort_column("SaleDate", False))
        tree.heading("TotalTicketsSold", text="Total Ticket Sold",
                     command=lambda: sort_column("TotalTicketsSold", False))

        for row in data:
            sale_date, total_tickets = row
            formatted_tickets = "{:,.0f}".format(total_tickets).replace(",", ".")
            tree.insert("", "end", values=(sale_date, formatted_tickets))

        self.hide_time_range_buttons()
        self.hide_time_range_totalrevenue()
        self.show_time_range_ticket()
    def ticket_daily(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        cursor = self.main.mydb.cursor()
        query = """
                SELECT
                  DATE(PayTime) AS SaleDate,
                  COUNT(TicketID) AS TotalTicketsSold
                FROM Payments
                GROUP BY DATE(PayTime)
                ORDER BY SaleDate desc;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("YearMonth", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.heading("YearMonth", text="Date")
        tree.heading("TotalRevenue", text="Total Ticket Sold")
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def sort_column(col, reverse):

            data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

            if col == "TotalRevenue":

                data_list.sort(key=lambda t: int(t[0].replace(".", "")), reverse=reverse)
            else:
                data_list.sort(key=lambda t: t[0], reverse=reverse)

            for index, (val, k) in enumerate(data_list):
                tree.move(k, '', index)

            tree.heading(col, command=lambda: sort_column(col, not reverse))

        tree.heading("YearMonth", text="Date", command=lambda: sort_column("YearMonth", False))
        tree.heading("TotalRevenue", text="Total Ticket Sold",
                     command=lambda: sort_column("TotalRevenue", False))

        for row in data:
            sale_date, total_tickets = row
            formatted_tickets = "{:,.0f}".format(total_tickets).replace(",", ".")
            tree.insert("", "end", values=(sale_date, formatted_tickets))
    def ticket_monthly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        cursor = self.main.mydb.cursor()
        query = """
                SELECT
                  DATE_FORMAT(PayTime, '%Y-%m') AS YearMonth,
                  COUNT(TicketID) AS TotalTicketsSold
                FROM Payments
                GROUP BY YearMonth
                ORDER BY YearMonth desc;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("YearMonth", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.heading("YearMonth", text="Date")
        tree.heading("TotalRevenue", text="Total Ticket Sold")
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def sort_column(col, reverse):

            data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

            if col == "TotalRevenue":

                data_list.sort(key=lambda t: int(t[0].replace(".", "")), reverse=reverse)
            else:
                data_list.sort(key=lambda t: t[0], reverse=reverse)

            for index, (val, k) in enumerate(data_list):
                tree.move(k, '', index)

            tree.heading(col, command=lambda: sort_column(col, not reverse))

        tree.heading("YearMonth", text="Date", command=lambda: sort_column("YearMonth", False))
        tree.heading("TotalRevenue", text="Total Ticket Sold",
                     command=lambda: sort_column("TotalRevenue", False))

        for row in data:
            sale_date, total_tickets = row
            formatted_tickets = "{:,.0f}".format(total_tickets).replace(",", ".")
            tree.insert("", "end", values=(sale_date, formatted_tickets))
    def ticket_quarterly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        cursor = self.main.mydb.cursor()
        query = """
                SELECT
                  CONCAT(Year, '-Q', Quarter) AS YearQuarter,
                  COUNT(*) AS TotalTicketsSold
                FROM (
                  SELECT 
                    TicketID,
                    YEAR(PayTime) AS Year,
                    QUARTER(PayTime) AS Quarter
                  FROM Payments
                ) AS sub
                GROUP BY Year, Quarter
                ORDER BY Year desc, Quarter desc;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("YearMonth", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.heading("YearMonth", text="Date")
        tree.heading("TotalRevenue", text="Total Ticket Sold")
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def sort_column(col, reverse):

            data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

            if col == "TotalRevenue":

                data_list.sort(key=lambda t: int(t[0].replace(".", "")), reverse=reverse)
            else:
                data_list.sort(key=lambda t: t[0], reverse=reverse)

            for index, (val, k) in enumerate(data_list):
                tree.move(k, '', index)

            tree.heading(col, command=lambda: sort_column(col, not reverse))

        tree.heading("YearMonth", text="Date", command=lambda: sort_column("YearMonth", False))
        tree.heading("TotalRevenue", text="Total Ticket Sold",
                     command=lambda: sort_column("TotalRevenue", False))

        for row in data:
            sale_date, total_tickets = row
            formatted_tickets = "{:,.0f}".format(total_tickets).replace(",", ".")
            tree.insert("", "end", values=(sale_date, formatted_tickets))
    def ticket_yearly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        self.graph_frame.update_idletasks()
        cursor = self.main.mydb.cursor()
        query = """
                SELECT
                    DATE_FORMAT(PayTime, '%Y') AS Year,
                    COUNT(TicketID) AS TotalTicketsSold
                FROM Payments
                GROUP BY Year
                ORDER BY Year DESC;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe = df.copy()

        table_frame = tk.Frame(self.graph_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("YearMonth", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        tree.heading("YearMonth", text="Date")
        tree.heading("TotalRevenue", text="Total Ticket Sold")
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        def sort_column(col, reverse):

            data_list = [(tree.set(k, col), k) for k in tree.get_children('')]

            if col == "TotalRevenue":

                data_list.sort(key=lambda t: int(t[0].replace(".", "")), reverse=reverse)
            else:
                data_list.sort(key=lambda t: t[0], reverse=reverse)

            for index, (val, k) in enumerate(data_list):
                tree.move(k, '', index)

            tree.heading(col, command=lambda: sort_column(col, not reverse))

        tree.heading("YearMonth", text="Date", command=lambda: sort_column("YearMonth", False))
        tree.heading("TotalRevenue", text="Total Ticket Sold",
                     command=lambda: sort_column("TotalRevenue", False))

        for row in data:
            sale_date, total_tickets = row
            formatted_tickets = "{:,.0f}".format(total_tickets).replace(",", ".")
            tree.insert("", "end", values=(sale_date, formatted_tickets))


    #DEF TAB2
    #Show/Hide button
    def hide_button2(self):
        self.hide_movie_button()
        self.hide_occupation()
        self.hide_screening()
        self.hide_day_button()
        self.hide_format_button()
    def show_movie_button(self):
        self.last_14days.pack(side="right", padx=10)
        self.last_30days.pack(side="right", padx=10)
        self.last_60days.pack(side="right", padx=10)
    def hide_movie_button(self):
        self.last_14days.pack_forget()
        self.last_30days.pack_forget()
        self.last_60days.pack_forget()
    def show_occupation(self):
        self.Occupation_table.pack(side="right", padx=10)
        self.Occupation_graph.pack(side="right", padx=10)
    def hide_occupation(self):
        self.Occupation_table.pack_forget()
        self.Occupation_graph.pack_forget()
    def show_screening(self):
        self.screening30.pack(side="right", padx=10)
        self.screening90.pack(side="right", padx=10)
        self.screening.pack(side="right", padx=10)
    def hide_screening(self):
        self.screening30.pack_forget()
        self.screening90.pack_forget()
        self.screening.pack_forget()
    def show_day_button(self):
        self.day_30.pack(side="right", padx=10)
        self.day_90.pack(side="right", padx=10)
        self.day_all.pack(side="right", padx=10)
    def hide_day_button(self):
        self.day_30.pack_forget()
        self.day_90.pack_forget()
        self.day_all.pack_forget()
    def show_format_button(self):
        self.format_30_bt.pack(side="right", padx=10)
        self.format_90_bt.pack(side="right", padx=10)
        self.format_year_bt.pack(side="right", padx=10)
        self.format_all_bt.pack(side="right", padx=10)
    def hide_format_button(self):
        self.format_30_bt.pack_forget()
        self.format_90_bt.pack_forget()
        self.format_year_bt.pack_forget()
        self.format_all_bt.pack_forget()
    #Movie
    def display_movie(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'currency':
                    try:
                        return float(val.replace("₫", "").replace(".", "").replace(",", ".").strip())
                    except ValueError:
                        return 0.0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT MovieID, MovieTitle, Genre, TicketsSold, TotalRevenue, AttendanceRate FROM movie_14days"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("MovieID", "MovieTitle", "Genre", "TicketsSold", "TotalRevenue", "AttendanceRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        col_types = {
            "MovieID": "int",
            "MovieTitle": "text",
            "Genre": "text",
            "TicketsSold": "int",
            "TotalRevenue": "currency",
            "AttendanceRate": "percentage"
        }

        headings = {
            "MovieID": "Movie ID",
            "MovieTitle": "Title",
            "Genre": "Genre",
            "TicketsSold": "Tickets Sold",
            "TotalRevenue": "Total Revenue",
            "AttendanceRate": "Attendance Rate"
        }

        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name != "MovieTitle" else 200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in records:
            movie_id, title, genre, tickets, revenue, attendance = row
            formatted_revenue = "{:,.0f} ₫".format(revenue).replace(",", ".")
            formatted_attendance = f"{attendance * 100:.2f}%"
            tree.insert("", "end", values=(movie_id, title, genre, tickets, formatted_revenue, formatted_attendance))

        self.hide_button2()
        self.show_movie_button()
    def display_movie14(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'currency':
                    try:
                        return float(val.replace("₫", "").replace(".", "").replace(",", ".").strip())
                    except ValueError:
                        return 0.0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT MovieID, MovieTitle, Genre, TicketsSold, TotalRevenue, AttendanceRate FROM movie_14days"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("MovieID", "MovieTitle", "Genre", "TicketsSold", "TotalRevenue", "AttendanceRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        col_types = {
            "MovieID": "int",
            "MovieTitle": "text",
            "Genre": "text",
            "TicketsSold": "int",
            "TotalRevenue": "currency",
            "AttendanceRate": "percentage"
        }

        headings = {
            "MovieID": "Movie ID",
            "MovieTitle": "Title",
            "Genre": "Genre",
            "TicketsSold": "Tickets Sold",
            "TotalRevenue": "Total Revenue",
            "AttendanceRate": "Attendance Rate"
        }

        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name != "MovieTitle" else 200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in records:
            movie_id, title, genre, tickets, revenue, attendance = row
            formatted_revenue = "{:,.0f} ₫".format(revenue).replace(",", ".")
            formatted_attendance = f"{attendance * 100:.2f}%"
            tree.insert("", "end", values=(movie_id, title, genre, tickets, formatted_revenue, formatted_attendance))
    def display_movie30(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'currency':
                    try:
                        return float(val.replace("₫", "").replace(".", "").replace(",", ".").strip())
                    except ValueError:
                        return 0.0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT MovieID, MovieTitle, Genre, TicketsSold, TotalRevenue, AttendanceRate FROM movie_30days"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("MovieID", "MovieTitle", "Genre", "TicketsSold", "TotalRevenue", "AttendanceRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        col_types = {
            "MovieID": "int",
            "MovieTitle": "text",
            "Genre": "text",
            "TicketsSold": "int",
            "TotalRevenue": "currency",
            "AttendanceRate": "percentage"
        }

        headings = {
            "MovieID": "Movie ID",
            "MovieTitle": "Title",
            "Genre": "Genre",
            "TicketsSold": "Tickets Sold",
            "TotalRevenue": "Total Revenue",
            "AttendanceRate": "Attendance Rate"
        }

        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name != "MovieTitle" else 200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in records:
            movie_id, title, genre, tickets, revenue, attendance = row
            formatted_revenue = "{:,.0f} ₫".format(revenue).replace(",", ".")
            formatted_attendance = f"{attendance * 100:.2f}%"
            tree.insert("", "end", values=(movie_id, title, genre, tickets, formatted_revenue, formatted_attendance))
    def display_movie60(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'currency':
                    try:
                        return float(val.replace("₫", "").replace(".", "").replace(",", ".").strip())
                    except ValueError:
                        return 0.0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT MovieID, MovieTitle, Genre, TicketsSold, TotalRevenue, AttendanceRate FROM movie_60days"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("MovieID", "MovieTitle", "Genre", "TicketsSold", "TotalRevenue", "AttendanceRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        col_types = {
            "MovieID": "int",
            "MovieTitle": "text",
            "Genre": "text",
            "TicketsSold": "int",
            "TotalRevenue": "currency",
            "AttendanceRate": "percentage"
        }

        headings = {
            "MovieID": "Movie ID",
            "MovieTitle": "Title",
            "Genre": "Genre",
            "TicketsSold": "Tickets Sold",
            "TotalRevenue": "Total Revenue",
            "AttendanceRate": "Attendance Rate"
        }

        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name != "MovieTitle" else 200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in records:
            movie_id, title, genre, tickets, revenue, attendance = row
            formatted_revenue = "{:,.0f} ₫".format(revenue).replace(",", ".")
            formatted_attendance = f"{attendance * 100:.2f}%"
            tree.insert("", "end", values=(movie_id, title, genre, tickets, formatted_revenue, formatted_attendance))
    #Occupation
    def display_occupation(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()
        self.sort_states = {}
        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT Month, Tickets_Sold, Total_Screenings, TotalSeat, `Occupation Rate (%)` FROM occupation"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("Month", "Tickets_Sold", "Total_Screenings", "TotalSeat", "OccupationRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        headings = {
            "Month": "Month",
            "Tickets_Sold": "Tickets Sold",
            "Total_Screenings": "Total Screenings",
            "TotalSeat": "Total Seats",
            "OccupationRate": "Occupancy Rate (%)"
        }
        col_types = {
            "Month": "text",
            "Tickets_Sold": "int",
            "Total_Screenings": "int",
            "TotalSeat": "int",
            "OccupationRate": "percentage"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=130 if col_name == "Total_Screenings" else 100 if col_name != "OccupationRate" else 150,
                        anchor="center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        for row in records:
            month, tickets_sold, total_screenings, total_seat, occupation_rate = row
            formatted_occupation = f"{occupation_rate:.2f}%"
            tree.insert("", "end", values=(month, tickets_sold, total_screenings, total_seat, formatted_occupation))

        self.hide_button2()
        self.show_occupation()
    def display_occupation_table(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()
        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT Month, Tickets_Sold, Total_Screenings, TotalSeat, `Occupation Rate (%)` FROM occupation"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("Month", "Tickets_Sold", "Total_Screenings", "TotalSeat", "OccupationRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        headings = {
            "Month": "Month",
            "Tickets_Sold": "Tickets Sold",
            "Total_Screenings": "Total Screenings",
            "TotalSeat": "Total Seats",
            "OccupationRate": "Occupation Rate (%)"
        }
        col_types = {
            "Month": "text",
            "Tickets_Sold": "int",
            "Total_Screenings": "int",
            "TotalSeat": "int",
            "OccupationRate": "percentage"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=130 if col_name == "Total_Screenings" else 100 if col_name != "OccupationRate" else 150,
                        anchor="center")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        for row in records:
            month, tickets_sold, total_screenings, total_seat, occupation_rate = row
            formatted_occupation = f"{occupation_rate:.2f}%"
            tree.insert("", "end", values=(month, tickets_sold, total_screenings, total_seat, formatted_occupation))
    def display_occupation_graph(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = "SELECT Month, Tickets_Sold, `Occupation Rate (%)` FROM occupation"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        data.sort(key=lambda row: row[0])
        months = [row[0] for row in data]
        tickets_sold = [row[1] for row in data]
        occupation_rates = [row[2] for row in data]

        fig, ax1 = plt.subplots(figsize=(11, 6), dpi=100)
        self.current_figure2 = fig

        ax1.bar(months, tickets_sold, color='skyblue', label='Tickets Sold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Tickets Sold', color='skyblue')
        ax1.tick_params(axis='y', labelcolor='skyblue')
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax1.set_xticks(range(0, len(months), 3))
        ax1.set_xticklabels(months[::3], rotation=45, ha='right')

        ax2 = ax1.twinx()
        ax2.plot(months, occupation_rates, color='darkgreen', marker='o', label='Occupation Rate (%)')
        ax2.set_ylabel('Occupancy Rate (%)', color='darkgreen')
        ax2.tick_params(axis='y', labelcolor='darkgreen')
        ax2.set_ylim(0, max(occupation_rates) + 1)

        plt.title('Monthly Tickets Sold and Occupation Rate')
        fig.autofmt_xdate()
        fig.tight_layout()
        plt.grid(True, axis='y', linestyle='--', alpha=0.5)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame2)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)
    #Screeningtime
    def display_screening_time(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()
        self.sort_states = {}
        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'currency':
                    try:
                        return float(val.replace("₫", "").replace(",", "").replace(".", "").strip())
                    except ValueError:
                        return 0.0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = ("SELECT ScreeningTime, TicketSold, OccupationRate, Revenue FROM screeningtime30")
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)
        columns = ("ScreeningTime", "TicketSold", "OccupationRate", "Revenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "ScreeningTime": "Screening Time",
            "TicketSold": "Tickets Sold",
            "OccupationRate": "Occupation Rate",
            "Revenue": "Revenue"
        }

        col_types = {
            "ScreeningTime": "text",
            "TicketSold": "int",
            "OccupationRate": "percentage",
            "Revenue": "currency"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name == "ScreeningTime" else 130, anchor="center")
        for row in records:
            screening_time, tickets_sold, occupation_rate, revenue = row
            formatted_occupation = f"{occupation_rate * 100:.1f}%"
            formatted_revenue = f"{int(revenue):,} ₫".replace(",", ".")
            tree.insert('', 'end', values=(screening_time, tickets_sold, formatted_occupation, formatted_revenue))

        self.hide_button2()
        self.show_screening()
    def display_screening30(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()
        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'currency':
                    try:
                        return float(val.replace("₫", "").replace(",", "").replace(".", "").strip())
                    except ValueError:
                        return 0.0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = ("SELECT ScreeningTime, TicketSold, OccupationRate, Revenue FROM screeningtime30")
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)
        columns = ("ScreeningTime", "TicketSold", "OccupationRate", "Revenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "ScreeningTime": "Screening Time",
            "TicketSold": "Tickets Sold",
            "OccupationRate": "Occupation Rate",
            "Revenue": "Revenue"
        }

        col_types = {
            "ScreeningTime": "text",
            "TicketSold": "int",
            "OccupationRate": "percentage",
            "Revenue": "currency"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name == "ScreeningTime" else 130, anchor="center")
        for row in records:
            screening_time, tickets_sold, occupation_rate, revenue = row
            formatted_occupation = f"{occupation_rate * 100:.1f}%"
            formatted_revenue = f"{int(revenue):,} ₫".replace(",", ".")
            tree.insert('', 'end', values=(screening_time, tickets_sold, formatted_occupation, formatted_revenue))
    def display_screening90(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()
        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'currency':
                    try:
                        return float(val.replace("₫", "").replace(",", "").replace(".", "").strip())
                    except ValueError:
                        return 0.0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = ("SELECT ScreeningTime, TicketSold, OccupationRate, Revenue FROM screeningtime90")
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)
        columns = ("ScreeningTime", "TicketSold", "OccupationRate", "Revenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "ScreeningTime": "Screening Time",
            "TicketSold": "Tickets Sold",
            "OccupationRate": "Occupation Rate",
            "Revenue": "Revenue"
        }

        col_types = {
            "ScreeningTime": "text",
            "TicketSold": "int",
            "OccupationRate": "percentage",
            "Revenue": "currency"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name == "ScreeningTime" else 130, anchor="center")
        for row in records:
            screening_time, tickets_sold, occupation_rate, revenue = row
            formatted_occupation = f"{occupation_rate * 100:.1f}%"
            formatted_revenue = f"{int(revenue):,} ₫".replace(",", ".")
            tree.insert('', 'end', values=(screening_time, tickets_sold, formatted_occupation, formatted_revenue))
    def display_screening(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()
        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                elif col_type == 'currency':
                    try:
                        return float(val.replace("₫", "").replace(",", "").replace(".", "").strip())
                    except ValueError:
                        return 0.0
                elif col_type == 'percentage':
                    try:
                        return float(val.replace("%", "").strip())
                    except ValueError:
                        return 0.0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, "", index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = ("SELECT ScreeningTime, TicketSold, OccupationRate, Revenue FROM screeningtime")
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)
        columns = ("ScreeningTime", "TicketSold", "OccupationRate", "Revenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "ScreeningTime": "Screening Time",
            "TicketSold": "Tickets Sold",
            "OccupationRate": "Occupation Rate",
            "Revenue": "Revenue"
        }

        col_types = {
            "ScreeningTime": "text",
            "TicketSold": "int",
            "OccupationRate": "percentage",
            "Revenue": "currency"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name == "ScreeningTime" else 130, anchor="center")
        for row in records:
            screening_time, tickets_sold, occupation_rate, revenue = row
            formatted_occupation = f"{occupation_rate * 100:.1f}%"
            formatted_revenue = f"{int(revenue):,} ₫".replace(",", ".")
            tree.insert('', 'end', values=(screening_time, tickets_sold, formatted_occupation, formatted_revenue))
    #Day
    def day_performance(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, '', index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT Day, TicketSold, MostPopularShowtime FROM day_performance30"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)
        columns = ("Day", "TicketSold", "MostPopularShowtime")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "Day": "Day",
            "TicketSold": "Tickets Sold",
            "MostPopularShowtime": "Most Popular Showtime"
        }

        col_types = {
            "Day": "text",
            "TicketSold": "int",
            "MostPopularShowtime": "text"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name == "Day" else 150, anchor="center")
        for row in records:
            tree.insert('', 'end', values=row)

        self.hide_button2()
        self.show_day_button()
    def display_day30(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, '', index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT Day, TicketSold, MostPopularShowtime FROM day_performance30"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)
        columns = ("Day", "TicketSold", "MostPopularShowtime")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "Day": "Day",
            "TicketSold": "Tickets Sold",
            "MostPopularShowtime": "Most Popular Showtime"
        }

        col_types = {
            "Day": "text",
            "TicketSold": "int",
            "MostPopularShowtime": "text"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name == "Day" else 150, anchor="center")
        for row in records:
            tree.insert('', 'end', values=row)
    def display_day90(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, '', index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT Day, TicketSold, MostPopularShowtime FROM day_performance90"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)
        columns = ("Day", "TicketSold", "MostPopularShowtime")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "Day": "Day",
            "TicketSold": "Tickets Sold",
            "MostPopularShowtime": "Most Popular Showtime"
        }

        col_types = {
            "Day": "text",
            "TicketSold": "int",
            "MostPopularShowtime": "text"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name == "Day" else 150, anchor="center")
        for row in records:
            tree.insert('', 'end', values=row)
    def display_day_all(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(val)
                    except ValueError:
                        return 0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children("")]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, '', index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT Day, TicketSold, MostPopularShowtime FROM day_performancealltime"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)
        columns = ("Day", "TicketSold", "MostPopularShowtime")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "Day": "Day",
            "TicketSold": "Tickets Sold",
            "MostPopularShowtime": "Most Popular Showtime"
        }

        col_types = {
            "Day": "text",
            "TicketSold": "int",
            "MostPopularShowtime": "text"
        }
        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120 if col_name == "Day" else 150, anchor="center")
        for row in records:
            tree.insert('', 'end', values=row)
    #Format
    def format_performance(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(float(val.replace(',', '').replace('₫', '').strip()))
                    except ValueError:
                        return 0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children('')]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, '', index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM genre_format_30"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("MovieGenre", "MovieFormat", "TotalTicketsSold", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "MovieGenre": "Genre",
            "MovieFormat": "Format",
            "TotalTicketsSold": "Tickets Sold",
            "TotalRevenue": "Revenue"
        }
        col_types = {
            "MovieGenre": "text",
            "MovieFormat": "text",
            "TotalTicketsSold": "int",
            "TotalRevenue": "int"
        }

        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120, anchor="center")


        for row in records:
            formatted_row = list(row)
            formatted_row[3] = f"{formatted_row[3]:,.0f} ₫"
            tree.insert('', 'end', values=formatted_row)

        self.hide_button2()
        self.show_format_button()
    def format_30(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(float(val.replace(',', '').replace('₫', '').strip()))
                    except ValueError:
                        return 0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children('')]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, '', index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM genre_format_30"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("MovieGenre", "MovieFormat", "TotalTicketsSold", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "MovieGenre": "Genre",
            "MovieFormat": "Format",
            "TotalTicketsSold": "Tickets Sold",
            "TotalRevenue": "Revenue"
        }
        col_types = {
            "MovieGenre": "text",
            "MovieFormat": "text",
            "TotalTicketsSold": "int",
            "TotalRevenue": "int"
        }

        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120, anchor="center")

        for row in records:
            formatted_row = list(row)
            formatted_row[3] = f"{formatted_row[3]:,.0f} ₫"
            tree.insert('', 'end', values=formatted_row)
    def format_90(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(float(val.replace(',', '').replace('₫', '').strip()))
                    except ValueError:
                        return 0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children('')]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, '', index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM genre_format_90"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("MovieGenre", "MovieFormat", "TotalTicketsSold", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "MovieGenre": "Genre",
            "MovieFormat": "Format",
            "TotalTicketsSold": "Tickets Sold",
            "TotalRevenue": "Revenue"
        }
        col_types = {
            "MovieGenre": "text",
            "MovieFormat": "text",
            "TotalTicketsSold": "int",
            "TotalRevenue": "int"
        }

        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120, anchor="center")

        for row in records:
            formatted_row = list(row)
            formatted_row[3] = f"{formatted_row[3]:,.0f} ₫"
            tree.insert('', 'end', values=formatted_row)
    def format_year(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(float(val.replace(',', '').replace('₫', '').strip()))
                    except ValueError:
                        return 0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children('')]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, '', index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM genre_format_year"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("MovieGenre", "MovieFormat", "TotalTicketsSold", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "MovieGenre": "Genre",
            "MovieFormat": "Format",
            "TotalTicketsSold": "Tickets Sold",
            "TotalRevenue": "Revenue"
        }
        col_types = {
            "MovieGenre": "text",
            "MovieFormat": "text",
            "TotalTicketsSold": "int",
            "TotalRevenue": "int"
        }

        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120, anchor="center")

        for row in records:
            formatted_row = list(row)
            formatted_row[3] = f"{formatted_row[3]:,.0f} ₫"
            tree.insert('', 'end', values=formatted_row)
    def format_all(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        self.graph_frame2.update_idletasks()

        self.sort_states = {}

        def sort_column(treeview, col, col_type):
            def clean_value(val):
                if col_type == 'int':
                    try:
                        return int(float(val.replace(',', '').replace('₫', '').strip()))
                    except ValueError:
                        return 0
                return val.lower() if isinstance(val, str) else val

            data = [(treeview.set(child, col), child) for child in treeview.get_children('')]
            reverse = self.sort_states.get(col, False)
            data.sort(key=lambda x: clean_value(x[0]), reverse=reverse)

            for index, (_, child) in enumerate(data):
                treeview.move(child, '', index)

            self.sort_states[col] = not reverse

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM genre_format_all"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe2 = df.copy()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("MovieGenre", "MovieFormat", "TotalTicketsSold", "TotalRevenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        headings = {
            "MovieGenre": "Genre",
            "MovieFormat": "Format",
            "TotalTicketsSold": "Tickets Sold",
            "TotalRevenue": "Revenue"
        }
        col_types = {
            "MovieGenre": "text",
            "MovieFormat": "text",
            "TotalTicketsSold": "int",
            "TotalRevenue": "int"
        }

        for col_name in columns:
            tree.heading(col_name, text=headings[col_name], command=lambda c=col_name: sort_column(tree, c, col_types[c]))
            tree.column(col_name, width=120, anchor="center")

        for row in records:
            formatted_row = list(row)
            formatted_row[3] = f"{formatted_row[3]:,.0f} ₫"
            tree.insert('', 'end', values=formatted_row)

    #DEF TAB3
    #Show/hide buttons
    def hide_button3(self):
        self.hide_age_button()
        self.hide_age_genre_button()
        self.hide_age_time_button()
        self.hide_age_format_button()
    def show_age_button(self):
        self.age_90.pack(side="right", padx=10)
        self.age_year.pack(side="right", padx=10)
        self.age_all.pack(side="right", padx=10)
    def hide_age_button(self):
        self.age_90.pack_forget()
        self.age_year.pack_forget()
        self.age_all.pack_forget()
    def show_age_genre_button(self):
        self.genre_17.pack(side="right", padx=10)
        self.genre_25.pack(side="right", padx=10)
        self.genre_40.pack(side="right", padx=10)
        self.genre_60.pack(side="right", padx=10)
        self.genre_above.pack(side="right", padx=10)
        self.genre_screening.pack(side="right", padx=10)
    def hide_age_genre_button(self):
        self.genre_17.pack_forget()
        self.genre_25.pack_forget()
        self.genre_40.pack_forget()
        self.genre_60.pack_forget()
        self.genre_above.pack_forget()
        self.genre_screening.pack_forget()
    def show_age_time_button(self):
        self.age_time_30_bt.pack(side="right", padx=10)
        self.age_time_90_bt.pack(side="right", padx=10)
        self.age_time_year_bt.pack(side="right", padx=10)
        self.age_time_all_bt.pack(side="right", padx=10)
    def hide_age_time_button(self):
        self.age_time_30_bt.pack_forget()
        self.age_time_90_bt.pack_forget()
        self.age_time_year_bt.pack_forget()
        self.age_time_all_bt.pack_forget()
    def show_age_format_button(self):
        self.age_format_30_bt.pack(side="right", padx=10)
        self.age_format_90_bt.pack(side="right", padx=10)
        self.age_format_year_bt.pack(side="right", padx=10)
        self.age_format_all_bt.pack(side="right", padx=10)
    def hide_age_format_button(self):
        self.age_format_30_bt.pack_forget()
        self.age_format_90_bt.pack_forget()
        self.age_format_year_bt.pack_forget()
        self.age_format_all_bt.pack_forget()
    #AGE
    def display_age(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        AgeRange, 
                        CustomerCount 
                    FROM 
                        age90
                    ORDER BY 
                        AgeRange;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['AgeRange'], df['CustomerCount'], color='green')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Age Range")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['AgeRange'])))
        ax.set_xticklabels(df['AgeRange'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

        self.hide_button3()
        self.show_age_button()
    def age90(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        AgeRange, 
                        CustomerCount 
                    FROM 
                        age90
                    ORDER BY 
                        AgeRange;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['AgeRange'], df['CustomerCount'], color='green')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Age Range")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['AgeRange'])))
        ax.set_xticklabels(df['AgeRange'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    def ageyear(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        AgeRange, 
                        CustomerCount 
                    FROM 
                        ageyear
                    ORDER BY 
                        AgeRange;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['AgeRange'], df['CustomerCount'], color='green')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Age Range")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['AgeRange'])))
        ax.set_xticklabels(df['AgeRange'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    def ageall(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        AgeRange, 
                        CustomerCount 
                    FROM 
                        age
                    ORDER BY 
                        AgeRange;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['AgeRange'], df['CustomerCount'], color='green')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Age Range")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['AgeRange'])))
        ax.set_xticklabels(df['AgeRange'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    #Genre-age
    def display_age_genre(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        Genre, 
                        TicketsSold 
                    FROM 
                        age17
                    ORDER BY 
                        Genre;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['Genre'], df['TicketsSold'], color='blue')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Genre")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['Genre'])))
        ax.set_xticklabels(df['Genre'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

        self.hide_button3()
        self.show_age_genre_button()
    def genre17(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        Genre, 
                        TicketsSold 
                    FROM 
                        age17
                    ORDER BY 
                        Genre;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['Genre'], df['TicketsSold'], color='blue')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Genre")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['Genre'])))
        ax.set_xticklabels(df['Genre'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    def genre25(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        Genre, 
                        TicketsSold 
                    FROM 
                        age25
                    ORDER BY 
                        Genre;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['Genre'], df['TicketsSold'], color='blue')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Genre")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['Genre'])))
        ax.set_xticklabels(df['Genre'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    def genre40(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        Genre, 
                        TicketsSold 
                    FROM 
                        age40
                    ORDER BY 
                        Genre;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['Genre'], df['TicketsSold'], color='blue')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Genre")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['Genre'])))
        ax.set_xticklabels(df['Genre'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    def genre60(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        Genre, 
                        TicketsSold 
                    FROM 
                        age60
                    ORDER BY 
                        Genre;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['Genre'], df['TicketsSold'], color='blue')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Genre")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['Genre'])))
        ax.set_xticklabels(df['Genre'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    def genre_above_60(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        query = """
                    SELECT 
                        Genre, 
                        TicketsSold 
                    FROM 
                        ageabove60
                    ORDER BY 
                        Genre;
                """

        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()
        fig = Figure(figsize=(11, 6), dpi=100)
        self.current_figure3 = fig
        ax = fig.add_subplot(111)

        ax.bar(df['Genre'], df['TicketsSold'], color='blue')

        ax.set_title("Customer Distribution by Age Range")
        ax.set_xlabel("Genre")
        ax.set_ylabel("Customer Count")
        ax.ticklabel_format(style='plain', axis='y')
        ax.set_xticks(range(len(df['Genre'])))
        ax.set_xticklabels(df['Genre'], rotation=45)
        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame3)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)
    def genre_screening_1(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query="SELECT * FROM genre_screening"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("Genre", "TotalScreenings")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("Genre", text="Genre")
        tree.heading("TotalScreenings", text="Total Screenings")
        tree.column("Genre", width=150, anchor="center")
        tree.column("TotalScreenings", width=150, anchor="center")

        for row in records:
            tree.insert('', 'end', values=row)
    #ScreeningTime-Age
    def display_time_age(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM age_time_30"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "ScreeningTime", "TicketCount")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("ScreeningTime", text="Screening Time")
        tree.heading("TicketCount", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("ScreeningTime", width=120, anchor="center")
        tree.column("TicketCount", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)

        self.hide_button3()
        self.show_age_time_button()
    def age_time_30(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM age_time_30"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "ScreeningTime", "TicketCount")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("ScreeningTime", text="Screening Time")
        tree.heading("TicketCount", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("ScreeningTime", width=120, anchor="center")
        tree.column("TicketCount", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)
    def age_time_90(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM age_time_90"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "ScreeningTime", "TicketCount")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("ScreeningTime", text="Screening Time")
        tree.heading("TicketCount", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("ScreeningTime", width=120, anchor="center")
        tree.column("TicketCount", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)
    def age_time_year(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM age_time_year"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "ScreeningTime", "TicketCount")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("ScreeningTime", text="Screening Time")
        tree.heading("TicketCount", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("ScreeningTime", width=120, anchor="center")
        tree.column("TicketCount", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)
    def age_time_all(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query="SELECT * FROM age_time_all"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "ScreeningTime", "TicketCount")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("ScreeningTime", text="Screening Time")
        tree.heading("TicketCount", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("ScreeningTime", width=120, anchor="center")
        tree.column("TicketCount", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)
    #Format-Age
    def display_format_age(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM age_format_30"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "MovieFormat", "TicketsSold")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("MovieFormat", text="Movie Format")
        tree.heading("TicketsSold", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("MovieFormat", width=120, anchor="center")
        tree.column("TicketsSold", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)

        self.hide_button3()
        self.show_age_format_button()
    def age_format_30(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM age_format_30"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "MovieFormat", "TicketsSold")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("MovieFormat", text="Movie Format")
        tree.heading("TicketsSold", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("MovieFormat", width=120, anchor="center")
        tree.column("TicketsSold", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)
    def age_format_90(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM age_format_90"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "MovieFormat", "TicketsSold")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("MovieFormat", text="Movie Format")
        tree.heading("TicketsSold", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("MovieFormat", width=120, anchor="center")
        tree.column("TicketsSold", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)
    def age_format_year(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query = "SELECT * FROM age_format_year"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()

        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "MovieFormat", "TicketsSold")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("MovieFormat", text="Movie Format")
        tree.heading("TicketsSold", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("MovieFormat", width=120, anchor="center")
        tree.column("TicketsSold", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)
    def age_format_all(self):
        for widget in self.graph_frame3.winfo_children():
            widget.destroy()
        self.graph_frame3.update_idletasks()

        cursor = self.main.mydb.cursor()
        query="SELECT * FROM age_format_all"
        cursor.execute(query)
        records = cursor.fetchall()
        cursor.close()
        df = pd.read_sql(query, self.main.mydb)
        self.current_dataframe3 = df.copy()


        table_frame = tk.Frame(self.graph_frame3)
        table_frame.pack(fill="both", expand=True)

        columns = ("AgeGroup", "MovieFormat", "TicketsSold")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        self.sort_orders = {col: False for col in columns}

        def sort_by_column(col):
            descending = self.sort_orders[col]
            self.sort_orders[col] = not descending

            sorted_records = sorted(records, key=lambda x: x[columns.index(col)], reverse=descending)

            for item in tree.get_children():
                tree.delete(item)
            for record in sorted_records:
                tree.insert('', 'end', values=record)

        tree.heading("AgeGroup", text="Age Group")
        tree.heading("MovieFormat", text="Movie Format")
        tree.heading("TicketsSold", text="Customer Count")
        tree.column("AgeGroup", width=100, anchor="center")
        tree.column("MovieFormat", width=120, anchor="center")
        tree.column("TicketsSold", width=100, anchor="center")

        for col in columns:
            tree.heading(col, text=col, command=lambda c=col: sort_by_column(c))
            tree.column(col, anchor="center", width=120)

        for row in records:
            tree.insert('', 'end', values=row)

if __name__ == "__main__":
    app=Liemora()
    app.mainloop()

