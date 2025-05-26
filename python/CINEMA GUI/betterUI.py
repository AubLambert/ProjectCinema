import tkinter as tk
import customtkinter
from customtkinter import *
from tkinter import messagebox, font, Label, Frame, Button, Toplevel
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
import os

	
customtkinter.set_appearance_mode("dark") 
base_dir = os.path.dirname(__file__)
class Liemora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LIEMORA Cinema Login")
        self.geometry("700x500")
        self.resizable(False, False)
        self.mydb = None
        self.timeslot_window = None
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
    
        frame = CTkFrame(canvas, bd=2, relief="solid", padx=25, pady=25)
        canvas.create_window(350, 250, window=frame)
    
        CTkLabel(frame, text="LIEMORA Cinema", font=("Helvetica", 14, "bold")).pack(pady=(0, 20))
        CTkLabel(frame, text="Account").pack()
        self.account_entry = CTkEntry(frame, width=30)
        self.account_entry.pack(pady=5)
    
        CTkLabel(frame, text="Password").pack()
        self.password_entry = CTkEntry(frame, show="*", width=30)
        self.password_entry.pack(pady=5)
    
        login_btn = CTkButton(frame, text="Login", width=10, command=self.login)
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
                    Movie(self, username)
            else:
                messagebox.showerror("Login Failed", "Error Occurred")

        except Error as e:
            messagebox.showerror("Login Failed", f"Invalid username or password.\n\n{e}")

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

    def logout(self):
        if self.main.mydb.is_connected():
            self.main.mydb.close()
        self.destroy()
        self.main.account_entry.delete(0, tk.END)
        self.main.password_entry.delete(0, tk.END)
        self.main.deiconify()

    def movie_ui(self):
        tk.Button(self, text="Logout", font=10, width=7, command=self.logout).grid(row=0, column=0, sticky="nw", padx=20, pady=20)

        titles = ["John Wick", "Edge of Tomorrow", "Interstellar", "Coco", "Parasite", "The Revenant"]
        images = images = [
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
            except Exception as e:
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

        now = datetime.now()
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

        tk.Button(self.timeslot_window, text="SELECT", font=("Helvetica", 12), width=14).place(relx=0.5, rely=0.92, anchor="center")

        self.timeslot_window.transient(self)
        self.timeslot_window.grab_set()

class Admin(tk.Toplevel):
    def __init__(self, main):
        super().__init__(main)
        self.title("Liemora's Report")
        self.geometry("1350x750")
        self.resizable(False, False)
        self.configure(bg="white")
        self.main = main
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Style configuration
        style = ttk.Style()
        style.theme_use('default')
        fixed_width = 20
        style.configure('TNotebook.Tab',width=fixed_width,padding=[0, 10],anchor='center',font=('Helvetica', 12, 'bold'))

        tab_control = ttk.Notebook(self)
        tab_control.pack(expand=True, fill='both')
        self.tab1 = ttk.Frame(tab_control)
        self.tab2 = ttk.Frame(tab_control)
        self.tab3 = ttk.Frame(tab_control)

        tab_control.add(self.tab1, text='Sales Overview')
        tab_control.add(self.tab2, text='Performance Report')
        tab_control.add(self.tab3, text='Placeholder text')

        for tab in (self.tab1, self.tab2, self.tab3):
            main_frame = tk.Frame(tab)
            main_frame.pack(fill="both", expand=True)

            left_frame = tk.Frame(main_frame, width=160, bg="lightgrey")
            left_frame.pack(side="left", fill="y")

            right_frame = tk.Frame(main_frame)
            right_frame.pack(side="right", fill="both", expand=True)

            #Button
            if tab == self.tab1:
                self.graph_frame = tk.Frame(right_frame)
                self.graph_frame.pack(fill="both", expand=True)
                self.buttons_frame = tk.Frame(right_frame)
                self.buttons_frame.pack(fill="x", pady=10)

                #Left buttons
                tk.Button(left_frame, text="Logout",width=20,height=2, command=self.logout).pack(pady=3,padx=5,side="bottom")
                tk.Button(left_frame, width=20, height=2, text="Total Revenue",command=self.display_total_revenue).pack(pady=3, padx=5)
                tk.Button(left_frame,width=20,height=2, text="Revenue Trends", command=self.display_revenue_sales_chart).pack(pady=3,padx=5)
                tk.Button(left_frame, text="Ticket Sold", width=20, height=2, command=self.display_ticket).pack(pady=3, padx=5)
                tk.Button(left_frame, text="Tickets Sold Trend", width=20, height=2,command=self.display_ticket_chart).pack(pady=3, padx=5)

                #Revenue and ticket trend buttons
                self.all_time_btn = tk.Button(self.buttons_frame, text="All time", width=20, height=2,
                                              command=lambda: self.update_chart_by_range("all"))
                self.last_year_btn = tk.Button(self.buttons_frame, text="Last year", width=20, height=2,
                                               command=lambda: self.update_chart_by_range("year"))
                self.last_6_months_btn = tk.Button(self.buttons_frame, text="Last 6 months", width=20, height=2,
                                                   command=lambda: self.update_chart_by_range("6m"))
                self.last_30_days_btn = tk.Button(self.buttons_frame, text="Last 30 days", width=20, height=2,
                                                  command=lambda: self.update_chart_by_range("30"))

                #Revenue
                self.revenue_daily_btn = tk.Button(self.buttons_frame, text="Daily",width=20,height=2,command=self.revenue_daily)
                self.revenue_monthly_btn = tk.Button(self.buttons_frame, text="Monthly", width=20, height=2,command=self.revenue_monthly)
                self.revenue_quarterly_btn = tk.Button(self.buttons_frame, text="Quarterly", width=20, height=2,command=self.revenue_quarterly)
                self.revenue_yearly_btn = tk.Button(self.buttons_frame, text="Yearly", width=20, height=2,command=self.revenue_yearly)

                #Ticket
                self.ticket_daily_btn = tk.Button(self.buttons_frame, text="Daily", width=20, height=2,command=self.ticket_daily)
                self.ticket_monthly_btn = tk.Button(self.buttons_frame, text="Monthly", width=20, height=2,command=self.ticket_monthly)
                self.ticket_quarterly_btn = tk.Button(self.buttons_frame, text="Quarterly", width=20, height=2,command=self.ticket_quarterly)
                self.ticket_yearly_btn = tk.Button(self.buttons_frame, text="Yearly", width=20, height=2,command=self.ticket_yearly)

            elif tab == self.tab2:
                tk.Button(left_frame, text="Logout",width=20,height=2, command=self.logout).pack(pady=3,padx=5,side="bottom")
                tk.Button(left_frame, text="Top Performing Movies", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="Occupation Rate", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
            elif tab == self.tab3:
                tk.Button(left_frame, text="Logout",width=20,height=2, command=self.logout).pack(pady=3,padx=5,side="bottom")
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)

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

    #DEF Show/hide buttons
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
            if df.empty:
                raise ValueError("No data found for chart.")
            df['Date'] = pd.to_datetime(df['Date'])

            fig = Figure(figsize=(11, 6), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(df['Date'], df['TotalRevenue'], marker='o', linestyle='-', color='green')
            ax.set_title("Revenue Over Last 30 Days")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Revenue")
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()

            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating chart: {e}")
        self.hide_time_range_ticket()
        self.hide_time_range_totalrevenue()
        self.show_time_range_button()
        self.chart_mode = "revenue"
        self.update_chart_by_range("30")

    def display_30_days_revenue(self):
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
            if df.empty:
                raise ValueError("No data found for chart.")
            df['Date'] = pd.to_datetime(df['Date'])

            fig = Figure(figsize=(11, 6), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(df['Date'], df['TotalRevenue'], marker='o', linestyle='-', color='green')
            ax.set_title("Revenue Over Last 30 Days")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Revenue")
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()

            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating chart: {e}")

    def display_6_months_revenue(self):
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
            if df.empty:
                raise ValueError("No data found for 6-month revenue.")
            df['Date'] = pd.to_datetime(df['Date'])

            fig = Figure(figsize=(11, 6), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(df['Date'], df['TotalRevenue'], marker='o', linestyle='-', color='green')
            ax.set_title("Revenue Over Last 6 Months")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Revenue")
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()

            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating 6-month chart: {e}")

    def display_year_revenue(self):
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
            if df.empty:
                raise ValueError("No data found for yearly revenue.")
            df['Date'] = pd.to_datetime(df['Date'])

            fig = Figure(figsize=(11, 6), dpi=100)
            ax = fig.add_subplot(111)
            ax.plot(df['Date'], df['TotalRevenue'], marker='o', linestyle='-', color='green')
            ax.set_title("Revenue Over Last Year")
            ax.set_xlabel("Date")
            ax.set_ylabel("Total Revenue")
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()


            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating yearly chart: {e}")

    def display_alltime_revenue(self):
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
            if df.empty:
                raise ValueError("No data found for all-time revenue.")

            fig = Figure(figsize=(11, 6), dpi=100)
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


            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating all-time chart: {e}")

    #ticket trend
    def display_ticket_chart(self):
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
            if df.empty:
                raise ValueError("No data found for ticket sales.")

            fig = Figure(figsize=(11, 6), dpi=100)
            ax = fig.add_subplot(111)


            ax.plot(df['Date'], df['TotalTicketsSold'], marker='o', linestyle='-', color='blue')
            ax.set_title("Tickets Sold (Last 30 Days)")
            ax.set_xlabel("Date")
            ax.set_ylabel("Tickets Sold")
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()

            for widget in self.graph_frame.winfo_children():
                widget.destroy()

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
            if df.empty:
                raise ValueError("No data found for ticket sales.")

            fig = Figure(figsize=(11, 6), dpi=100)
            ax = fig.add_subplot(111)


            ax.plot(df['Date'], df['TotalTicketsSold'], marker='o', linestyle='-', color='blue')
            ax.set_title("Tickets Sold (Last 30 Days)")
            ax.set_xlabel("Date")
            ax.set_ylabel("Tickets Sold")
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()


            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load ticket sales chart.\n{str(e)}")

    def display_ticket_6months(self):
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
            if df.empty:
                raise ValueError("No data found for ticket sales.")

            fig = Figure(figsize=(11, 6), dpi=100)
            ax = fig.add_subplot(111)


            ax.plot(df['Date'], df['TotalTicketsSold'], marker='o', linestyle='-', color='blue')
            ax.set_title("Tickets Sold (Last 30 Days)")
            ax.set_xlabel("Date")
            ax.set_ylabel("Tickets Sold")
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()


            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load ticket sales chart.\n{str(e)}")

    def display_ticket_year(self):
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
            if df.empty:
                raise ValueError("No data found for ticket sales.")

            fig = Figure(figsize=(11, 6), dpi=100)
            ax = fig.add_subplot(111)


            ax.plot(df['Date'], df['TotalTicketsSold'], marker='o', linestyle='-', color='blue')
            ax.set_title("Tickets Sold (Last 30 Days)")
            ax.set_xlabel("Date")
            ax.set_ylabel("Tickets Sold")
            ax.set_xticks(range(len(df['Date'])))
            ax.set_xticklabels(df['Date'], rotation=45)
            ax.ticklabel_format(style='plain', axis='y')
            fig.autofmt_xdate()
            fig.tight_layout()


            for widget in self.graph_frame.winfo_children():
                widget.destroy()

            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Could not load ticket sales chart.\n{str(e)}")

    def display_ticket_alltime(self):
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
            if df.empty:
                raise ValueError("No data found for all-time ticket sold.")

            fig = Figure(figsize=(11, 6), dpi=100)
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


            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(pady=20)
        except Exception as e:
            print(f"Error generating all-time chart: {e}")

    #Revenue
    def display_total_revenue(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
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

        self.hide_time_range_buttons()
        self.hide_time_range_ticket()
        self.show_time_range_totalrevenue()

    def revenue_daily(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
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

    def revenue_quarterly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
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

    def revenue_yearly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
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

    #Ticket
    def display_ticket(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
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
            formatted_revenue = "{:,.0f}".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))

        self.hide_time_range_buttons()
        self.hide_time_range_totalrevenue()
        self.show_time_range_ticket()

    def ticket_daily(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
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
            formatted_revenue = "{:,.0f}".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))

    def ticket_monthly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
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
            formatted_revenue = "{:,.0f}".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))

    def ticket_quarterly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
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
            formatted_revenue = "{:,.0f}".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))

    def ticket_yearly(self):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        cursor = self.main.mydb.cursor()
        query = """
                SELECT
                  Year,
                  COUNT(*) AS TotalTicketsSold
                FROM (
                  SELECT 
                    TicketID,
                    YEAR(PayTime) AS Year
                  FROM Payments
                ) AS sub
                GROUP BY Year
                ORDER BY Year DESC;
                """
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

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
            formatted_revenue = "{:,.0f}".format(total_revenue).replace(",", ".")
            tree.insert("", "end", values=(year_month, formatted_revenue))

    #DEF TAB2


if __name__ == "__main__":
    app=Liemora()
    app.mainloop()

