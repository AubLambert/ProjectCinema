import tkinter as tk
from tkinter import messagebox, font, Label, Frame, Button, Toplevel
from PIL import Image, ImageTk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

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
        bg_image = Image.open(r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Cat.jpg").resize((700, 500), Image.LANCZOS)
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
        self.movie_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if self.main.mydb.is_connected():
            self.main.mydb.close()
        self.destroy()
        self.main.destroy()

    def movie_ui(self):
        tk.Button(self, text="Logout", font=10, width=7, command=self.logout).grid(row=0, column=0, sticky="nw",
                                                                                   padx=20, pady=20)

        grid_frame = tk.Frame(self, bg="white")
        grid_frame.place(relx=0.5, rely=0.55, anchor="center")

        titles = ["John Weed", "Edge of Tomorrow", "Interstellar", "Coco", "Parasite", "The Revenant"]
        images = [r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Interstellar.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg",
                  r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg"] # Đổi lại path của ảnh

        for i, (title, img_path) in enumerate(zip(titles, images)):
            img = Image.open(img_path).resize((180, 230))
            img = ImageTk.PhotoImage(img)

            btn = tk.Button(grid_frame, image=img, width=180, height=230,
                            command=lambda t=title: self.show_timeslots(t))
            btn.image = img
            btn.grid(row=(i // 3) * 2, column=i % 3, padx=20, pady=10)

            tk.Label(grid_frame, text=title, bg="white").grid(row=(i // 3) * 2 + 1, column=i % 3, pady=10)

    def show_timeslots(self, movie_title):
        ts_window = tk.Toplevel(self)
        ts_window.title(f"Timeslots for {movie_title}")
        ts_window.geometry("500x400")
        tk.Label(ts_window, text=f"Timeslots for '{movie_title}'", font=14).pack(pady=20)
        for time in ["8:00 AM", "14:00 PM", "20:00 PM"]:
            tk.Button(ts_window, text=time, width=15).pack(pady=5)
        ts_window.transient(self)
        ts_window.grab_set()

    def logout(self):
        self.main.mydb.close()
        self.destroy()
        self.main.account_entry.delete(0, tk.END)
        self.main.password_entry.delete(0, tk.END)
        self.main.deiconify()

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
        fixed_width = 17
        style.configure('TNotebook.Tab',width=fixed_width,padding=[0, 10],anchor='center',font=('Helvetica', 12, 'bold'))

        tab_control = ttk.Notebook(self)
        tab_control.pack(expand=True, fill='both')
        self.tab1 = ttk.Frame(tab_control)
        self.tab2 = ttk.Frame(tab_control)
        self.tab3 = ttk.Frame(tab_control)

        tab_control.add(self.tab1, text='Sales Overview')
        tab_control.add(self.tab2, text='Room Utilization')
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

                tk.Button(left_frame, text="Logout",width=20,height=2, command=self.logout).pack(pady=3,padx=5)
                tk.Button(left_frame, width=20, height=2, text="Total Revenue",
                          command=self.display_total_revenue).pack(pady=3, padx=5)
                tk.Button(left_frame,width=20,height=2, text="Revenue Trends", command=self.display_revenue_sales_chart).pack(pady=3,padx=5)
                tk.Button(left_frame, text="Tickets Sold Trend", width=20, height=2,command=self.display_ticket_chart).pack(pady=3, padx=5)
                self.all_time_btn = tk.Button(self.buttons_frame, text="All time", width=20, height=2,state="disabled",
                                              command=lambda: self.update_chart_by_range("all"))
                self.last_year_btn = tk.Button(self.buttons_frame, text="Last year", width=20, height=2,state="disabled",
                                               command=lambda: self.update_chart_by_range("year"))
                self.last_6_months_btn = tk.Button(self.buttons_frame, text="Last 6 months", width=20, height=2,state="disabled",
                                                   command=lambda: self.update_chart_by_range("6m"))
                self.last_30_days_btn = tk.Button(self.buttons_frame, text="Last 30 days", width=20, height=2, state="disabled",
                                                  command=lambda: self.update_chart_by_range("30"))
                self.last_30_days_btn.pack(side="right", padx=10)
                self.last_6_months_btn.pack(side="right", padx=10)
                self.last_year_btn.pack(side="right", padx=10)
                self.all_time_btn.pack(side="right", padx=10)
            elif tab == self.tab2:
                tk.Button(left_frame, text="Logout",width=20,height=2, command=self.logout).pack(pady=3,padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
            elif tab == self.tab3:
                tk.Button(left_frame, text="Logout",width=20,height=2, command=self.logout).pack(pady=3,padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)

    #DEF
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
        self.last_6_months_btn.config(state="normal")
        self.last_year_btn.config(state="normal")
        self.all_time_btn.config(state="normal")
        self.last_30_days_btn.config(state="normal")
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

        self.last_6_months_btn.config(state="normal")
        self.last_year_btn.config(state="normal")
        self.all_time_btn.config(state="normal")
        self.last_30_days_btn.config(state="normal")
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
        tree.heading("YearMonth", text="Year-Month")
        tree.heading("TotalRevenue", text="Total Revenue")
        tree.column("YearMonth", width=150, anchor="center")
        tree.column("TotalRevenue", width=200, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        for row in data:
            year_month, total_revenue = row
            tree.insert("", "end", values=(year_month, total_revenue))

        self.last_6_months_btn.config(state="disabled")
        self.last_year_btn.config(state="disabled")
        self.all_time_btn.config(state="disabled")
        self.last_30_days_btn.config(state="disabled")

if __name__ == "__main__":
    app=Liemora()
    app.mainloop()

