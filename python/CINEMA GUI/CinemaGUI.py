import tkinter as tk
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
from matplotlib.ticker import MaxNLocator

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
        bg_image = Image.open(r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\CINEMA GUI\Images\Cat.jpg").resize((700, 500), Image.LANCZOS)
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
        images = [r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Cat.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Cat.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Cat.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Cat.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Cat.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Cat.jpg"]

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
        tab_control.add(self.tab3, text='Customer Insight')

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
                self.graph_frame2 = tk.Frame(right_frame)
                self.graph_frame2.pack(fill="both", expand=True)
                self.buttons_frame2 = tk.Frame(right_frame)
                self.buttons_frame2.pack(fill="x", pady=10)

                tk.Button(left_frame, text="Logout",width=20,height=2, command=self.logout).pack(pady=3,padx=5,side="bottom")
                tk.Button(left_frame, text="Movie Performance", width=20, height=2,command=self.display_movie).pack(pady=3, padx=5)
                tk.Button(left_frame, text="Occupation Rate", width=20, height=2, command=self.display_occupation).pack(pady=3, padx=5)
                tk.Button(left_frame, text="Screening Time", width=20, height=2,command=self.display_screeningtime).pack(pady=3, padx=5)
                tk.Button(left_frame, text="Weekday Performance", width=20, height=2,command=self.day_performance).pack(pady=3, padx=5)

                #Movies
                self.last_14days = tk.Button(self.buttons_frame2, text="Last 14 days", width=20, height=2,command=self.display_movie14)
                self.last_30days = tk.Button(self.buttons_frame2, text="Last 30 days", width=20, height=2,command=self.display_movie30)
                self.last_60days = tk.Button(self.buttons_frame2, text="Last 60 days", width=20, height=2,command=self.display_movie60)

                #Occupation
                self.Occupation_table = tk.Button(self.buttons_frame2, text="Table", width=20, height=2,
                                             command=self.display_occupation_table)
                self.Occupation_graph = tk.Button(self.buttons_frame2, text="Graph", width=20, height=2,
                                                  command=self.display_occupation_graph)

                #Screening
                self.screening30 = tk.Button(self.buttons_frame2, text="Last 30 days", width=20, height=2,
                                             command=self.display_screening30)
                self.screening90 = tk.Button(self.buttons_frame2, text="Last 90 days", width=20, height=2,
                                           command=self.display_screening90)
                self.screening = tk.Button(self.buttons_frame2, text="All time", width=20, height=2,
                                           command=self.display_screening)
                #Day Performance
                self.day_30 = tk.Button(self.buttons_frame2, text="Last 30 days", width=20, height=2,
                                             command=self.display_day30)
                self.day_90 = tk.Button(self.buttons_frame2, text="Last 90 days", width=20, height=2,
                                             command=self.display_day90)
                self.day_all = tk.Button(self.buttons_frame2, text="All time", width=20, height=2,
                                             command=self.display_day_all)

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
            ax.set_title("Tickets Sold Over Last 30 Days")
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
            ax.set_title("Tickets Sold Over Last 30 Days")
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
            ax.set_title("Tickets Sold Over Last 6 Months")
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
            ax.set_title("Tickets Sold Over Last Year")
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
        tree.heading("TotalRevenue", text="Total Ticket Sold")
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
        tree.heading("TotalRevenue", text="Total Ticket Sold")
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
        tree.heading("TotalRevenue", text="Total Ticket Sold")
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
        tree.heading("TotalRevenue", text="Total Ticket Sold")
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
                    DATE_FORMAT(PayTime, '%Y') AS Year,
                    COUNT(TicketID) AS TotalTicketsSold
                FROM Payments
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
        tree.heading("TotalRevenue", text="Total Ticket Sold")
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
    #Show/Hide button
    def hide_button2(self):
        self.hide_movie_button()
        self.hide_occupation()
        self.hide_screening()
        self.hide_day_button()
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


    #Movie
    def display_movie(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        query = "SELECT MovieID, MovieTitle, Genre, TicketsSold, TotalRevenue, AttendanceRate FROM movie_14days"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("MovieID", "MovieTitle", "Genre", "TicketsSold", "TotalRevenue", "AttendanceRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        tree.heading("MovieID", text="Movie ID")
        tree.heading("MovieTitle", text="Title")
        tree.heading("Genre", text="Genre")
        tree.heading("TicketsSold", text="Tickets Sold")
        tree.heading("TotalRevenue", text="Total Revenue")
        tree.heading("AttendanceRate", text="Attendance Rate")

        tree.column("MovieID", width=80, anchor="center")
        tree.column("MovieTitle", width=200, anchor="center")
        tree.column("Genre", width=100, anchor="center")
        tree.column("TicketsSold", width=100, anchor="center")
        tree.column("TotalRevenue", width=150, anchor="center")
        tree.column("AttendanceRate", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in data:
            movie_id, title, genre, tickets, revenue, attendance = row
            formatted_revenue = "{:,.0f} ₫".format(revenue).replace(",", ".")
            formatted_attendance = f"{attendance * 100:.2f}%"
            tree.insert("", "end", values=(movie_id, title, genre, tickets, formatted_revenue, formatted_attendance))

        self.hide_button2()
        self.show_movie_button()
    def display_movie14(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        query = "SELECT MovieID, MovieTitle, Genre, TicketsSold, TotalRevenue, AttendanceRate FROM movie_14days"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("MovieID", "MovieTitle", "Genre", "TicketsSold", "TotalRevenue", "AttendanceRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        tree.heading("MovieID", text="Movie ID")
        tree.heading("MovieTitle", text="Title")
        tree.heading("Genre", text="Genre")
        tree.heading("TicketsSold", text="Tickets Sold")
        tree.heading("TotalRevenue", text="Total Revenue")
        tree.heading("AttendanceRate", text="Attendance Rate")

        tree.column("MovieID", width=80, anchor="center")
        tree.column("MovieTitle", width=200, anchor="center")
        tree.column("Genre", width=100, anchor="center")
        tree.column("TicketsSold", width=100, anchor="center")
        tree.column("TotalRevenue", width=150, anchor="center")
        tree.column("AttendanceRate", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in data:
            movie_id, title, genre, tickets, revenue, attendance = row
            formatted_revenue = "{:,.0f} ₫".format(revenue).replace(",", ".")
            formatted_attendance = f"{attendance * 100:.2f}%"
            tree.insert("", "end", values=(movie_id, title, genre, tickets, formatted_revenue, formatted_attendance))
    def display_movie30(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        query = "SELECT MovieID, MovieTitle, Genre, TicketsSold, TotalRevenue, AttendanceRate FROM movie_30days"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("MovieID", "MovieTitle", "Genre", "TicketsSold", "TotalRevenue", "AttendanceRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        tree.heading("MovieID", text="Movie ID")
        tree.heading("MovieTitle", text="Title")
        tree.heading("Genre", text="Genre")
        tree.heading("TicketsSold", text="Tickets Sold")
        tree.heading("TotalRevenue", text="Total Revenue")
        tree.heading("AttendanceRate", text="Attendance Rate")

        tree.column("MovieID", width=80, anchor="center")
        tree.column("MovieTitle", width=200, anchor="center")
        tree.column("Genre", width=100, anchor="center")
        tree.column("TicketsSold", width=100, anchor="center")
        tree.column("TotalRevenue", width=150, anchor="center")
        tree.column("AttendanceRate", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in data:
            movie_id, title, genre, tickets, revenue, attendance = row
            formatted_revenue = "{:,.0f} ₫".format(revenue).replace(",", ".")
            formatted_attendance = f"{attendance * 100:.2f}%"
            tree.insert("", "end", values=(movie_id, title, genre, tickets, formatted_revenue, formatted_attendance))
    def display_movie60(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        query = "SELECT MovieID, MovieTitle, Genre, TicketsSold, TotalRevenue, AttendanceRate FROM movie_60days"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        columns = ("MovieID", "MovieTitle", "Genre", "TicketsSold", "TotalRevenue", "AttendanceRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        tree.heading("MovieID", text="Movie ID")
        tree.heading("MovieTitle", text="Title")
        tree.heading("Genre", text="Genre")
        tree.heading("TicketsSold", text="Tickets Sold")
        tree.heading("TotalRevenue", text="Total Revenue")
        tree.heading("AttendanceRate", text="Attendance Rate")

        tree.column("MovieID", width=80, anchor="center")
        tree.column("MovieTitle", width=200, anchor="center")
        tree.column("Genre", width=100, anchor="center")
        tree.column("TicketsSold", width=100, anchor="center")
        tree.column("TotalRevenue", width=150, anchor="center")
        tree.column("AttendanceRate", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in data:
            movie_id, title, genre, tickets, revenue, attendance = row
            formatted_revenue = "{:,.0f} ₫".format(revenue).replace(",", ".")
            formatted_attendance = f"{attendance * 100:.2f}%"
            tree.insert("", "end", values=(movie_id, title, genre, tickets, formatted_revenue, formatted_attendance))
    #Occupation
    def display_occupation(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        query = "SELECT Month, Tickets_Sold, Total_Screenings, TotalSeat, `Occupation Rate (%)` FROM occupation"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Month", "Tickets_Sold", "Total_Screenings", "TotalSeat", "OccupationRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        tree.heading("Month", text="Month")
        tree.heading("Tickets_Sold", text="Tickets Sold")
        tree.heading("Total_Screenings", text="Total Screenings")
        tree.heading("TotalSeat", text="Total Seats")
        tree.heading("OccupationRate", text="Occupation Rate (%)")

        tree.column("Month", width=100, anchor="center")
        tree.column("Tickets_Sold", width=100, anchor="center")
        tree.column("Total_Screenings", width=130, anchor="center")
        tree.column("TotalSeat", width=100, anchor="center")
        tree.column("OccupationRate", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in data:
            month, tickets_sold, total_screenings, total_seat, occupation_rate = row
            formatted_occupation = f"{occupation_rate:.2f}%"
            tree.insert("", "end", values=(month, tickets_sold, total_screenings, total_seat, formatted_occupation))

        self.hide_button2()
        self.show_occupation()
    def display_occupation_table(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        query = "SELECT Month, Tickets_Sold, Total_Screenings, TotalSeat, `Occupation Rate (%)` FROM occupation"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Month", "Tickets_Sold", "Total_Screenings", "TotalSeat", "OccupationRate")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        tree.heading("Month", text="Month")
        tree.heading("Tickets_Sold", text="Tickets Sold")
        tree.heading("Total_Screenings", text="Total Screenings")
        tree.heading("TotalSeat", text="Total Seats")
        tree.heading("OccupationRate", text="Occupation Rate (%)")

        tree.column("Month", width=100, anchor="center")
        tree.column("Tickets_Sold", width=100, anchor="center")
        tree.column("Total_Screenings", width=130, anchor="center")
        tree.column("TotalSeat", width=100, anchor="center")
        tree.column("OccupationRate", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in data:
            month, tickets_sold, total_screenings, total_seat, occupation_rate = row
            formatted_occupation = f"{occupation_rate:.2f}%"
            tree.insert("", "end", values=(month, tickets_sold, total_screenings, total_seat, formatted_occupation))
    def display_occupation_graph(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        query = "SELECT Month, Tickets_Sold, `Occupation Rate (%)` FROM occupation"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        data.sort(key=lambda row: row[0])
        months = [row[0] for row in data]
        tickets_sold = [row[1] for row in data]
        occupation_rates = [row[2] for row in data]

        fig, ax1 = plt.subplots(figsize=(11, 6), dpi=100)

        ax1.bar(months, tickets_sold, color='skyblue', label='Tickets Sold')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Tickets Sold', color='skyblue')
        ax1.tick_params(axis='y', labelcolor='skyblue')
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax1.set_xticks(range(0, len(months), 3))
        ax1.set_xticklabels(months[::3], rotation=45, ha='right')

        ax2 = ax1.twinx()
        ax2.plot(months, occupation_rates, color='darkgreen', marker='o', label='Occupation Rate (%)')
        ax2.set_ylabel('Occupation Rate (%)', color='darkgreen')
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
    def display_screeningtime(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        cursor.execute("SELECT ScreeningTime, TicketSold, OccupationRate, Revenue FROM screeningtime30")
        records = cursor.fetchall()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("ScreeningTime", "TicketSold", "OccupationRate", "Revenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("ScreeningTime", text="Screening Time")
        tree.heading("TicketSold", text="Tickets Sold")
        tree.heading("OccupationRate", text="Occupation Rate")
        tree.heading("Revenue", text="Revenue")

        tree.column("ScreeningTime", width=120, anchor="center")
        tree.column("TicketSold", width=100, anchor="center")
        tree.column("OccupationRate", width=130, anchor="center")
        tree.column("Revenue", width=140, anchor="center")

        for row in records:
            screening_time, tickets_sold, occupation_rate, revenue = row

            formatted_occupation = f"{occupation_rate * 100:.1f}%"
            formatted_revenue = f"{int(revenue):,} ₫"

            tree.insert('', 'end', values=(
                screening_time,
                tickets_sold,
                formatted_occupation,
                formatted_revenue
            ))

        cursor.close()
        self.hide_button2()
        self.show_screening()
    def display_screening30(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        cursor.execute("SELECT ScreeningTime, TicketSold, OccupationRate, Revenue FROM screeningtime30")
        records = cursor.fetchall()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("ScreeningTime", "TicketSold", "OccupationRate", "Revenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("ScreeningTime", text="Screening Time")
        tree.heading("TicketSold", text="Tickets Sold")
        tree.heading("OccupationRate", text="Occupation Rate")
        tree.heading("Revenue", text="Revenue")

        tree.column("ScreeningTime", width=120, anchor="center")
        tree.column("TicketSold", width=100, anchor="center")
        tree.column("OccupationRate", width=130, anchor="center")
        tree.column("Revenue", width=140, anchor="center")

        for row in records:
            screening_time, tickets_sold, occupation_rate, revenue = row

            formatted_occupation = f"{occupation_rate * 100:.1f}%"
            formatted_revenue = f"{int(revenue):,} ₫"

            tree.insert('', 'end', values=(
                screening_time,
                tickets_sold,
                formatted_occupation,
                formatted_revenue
            ))

        cursor.close()
    def display_screening90(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        cursor.execute("SELECT ScreeningTime, TicketSold, OccupationRate, Revenue FROM screeningtime90")
        records = cursor.fetchall()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("ScreeningTime", "TicketSold", "OccupationRate", "Revenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("ScreeningTime", text="Screening Time")
        tree.heading("TicketSold", text="Tickets Sold")
        tree.heading("OccupationRate", text="Occupation Rate")
        tree.heading("Revenue", text="Revenue")

        tree.column("ScreeningTime", width=120, anchor="center")
        tree.column("TicketSold", width=100, anchor="center")
        tree.column("OccupationRate", width=130, anchor="center")
        tree.column("Revenue", width=140, anchor="center")

        for row in records:
            screening_time, tickets_sold, occupation_rate, revenue = row

            formatted_occupation = f"{occupation_rate * 100:.1f}%"
            formatted_revenue = f"{int(revenue):,} ₫"

            tree.insert('', 'end', values=(
                screening_time,
                tickets_sold,
                formatted_occupation,
                formatted_revenue
            ))

        cursor.close()
    def display_screening(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()

        cursor = self.main.mydb.cursor()
        cursor.execute("SELECT ScreeningTime, TicketSold, OccupationRate, Revenue FROM screeningtime")
        records = cursor.fetchall()

        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("ScreeningTime", "TicketSold", "OccupationRate", "Revenue")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("ScreeningTime", text="Screening Time")
        tree.heading("TicketSold", text="Tickets Sold")
        tree.heading("OccupationRate", text="Occupation Rate")
        tree.heading("Revenue", text="Revenue")

        tree.column("ScreeningTime", width=120, anchor="center")
        tree.column("TicketSold", width=100, anchor="center")
        tree.column("OccupationRate", width=130, anchor="center")
        tree.column("Revenue", width=140, anchor="center")

        for row in records:
            screening_time, tickets_sold, occupation_rate, revenue = row

            formatted_occupation = f"{occupation_rate * 100:.1f}%"
            formatted_revenue = f"{int(revenue):,} ₫"

            tree.insert('', 'end', values=(
                screening_time,
                tickets_sold,
                formatted_occupation,
                formatted_revenue
            ))

        cursor.close()
    #Day
    def day_performance(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        cursor = self.main.mydb.cursor()
        cursor.execute("SELECT Day, TicketSold, MostPopularShowtime FROM day_performance30")
        records = cursor.fetchall()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("Day", "TicketSold", "MostPopularShowtime")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("Day", text="Day")
        tree.heading("TicketSold", text="Tickets Sold")
        tree.heading("MostPopularShowtime", text="Most Popular Showtime")
        tree.column("Day", width=120, anchor="center")
        tree.column("TicketSold", width=100, anchor="center")
        tree.column("MostPopularShowtime", width=150, anchor="center")

        for row in records:
            tree.insert('', 'end', values=row)

        cursor.close()

        self.hide_button2()
        self.show_day_button()
    def display_day30(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        cursor = self.main.mydb.cursor()
        cursor.execute("SELECT Day, TicketSold, MostPopularShowtime FROM day_performance30")
        records = cursor.fetchall()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("Day", "TicketSold", "MostPopularShowtime")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("Day", text="Day")
        tree.heading("TicketSold", text="Tickets Sold")
        tree.heading("MostPopularShowtime", text="Most Popular Showtime")
        tree.column("Day", width=120, anchor="center")
        tree.column("TicketSold", width=100, anchor="center")
        tree.column("MostPopularShowtime", width=150, anchor="center")

        for row in records:
            tree.insert('', 'end', values=row)

        cursor.close()
    def display_day90(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        cursor = self.main.mydb.cursor()
        cursor.execute("SELECT Day, TicketSold, MostPopularShowtime FROM day_performance90")
        records = cursor.fetchall()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("Day", "TicketSold", "MostPopularShowtime")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("Day", text="Day")
        tree.heading("TicketSold", text="Tickets Sold")
        tree.heading("MostPopularShowtime", text="Most Popular Showtime")
        tree.column("Day", width=120, anchor="center")
        tree.column("TicketSold", width=100, anchor="center")
        tree.column("MostPopularShowtime", width=150, anchor="center")

        for row in records:
            tree.insert('', 'end', values=row)

        cursor.close()
    def display_day_all(self):
        for widget in self.graph_frame2.winfo_children():
            widget.destroy()
        cursor = self.main.mydb.cursor()
        cursor.execute("SELECT Day, TicketSold, MostPopularShowtime FROM day_performancealltime")
        records = cursor.fetchall()
        table_frame = tk.Frame(self.graph_frame2)
        table_frame.pack(fill="both", expand=True)

        columns = ("Day", "TicketSold", "MostPopularShowtime")
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=10)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("Day", text="Day")
        tree.heading("TicketSold", text="Tickets Sold")
        tree.heading("MostPopularShowtime", text="Most Popular Showtime")
        tree.column("Day", width=120, anchor="center")
        tree.column("TicketSold", width=100, anchor="center")
        tree.column("MostPopularShowtime", width=150, anchor="center")

        for row in records:
            tree.insert('', 'end', values=row)

        cursor.close()




if __name__ == "__main__":
    app=Liemora()
    app.mainloop()

