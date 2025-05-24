import tkinter as tk
from tkinter import messagebox, font, Label, Frame, Button, Toplevel
from PIL import Image, ImageTk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error
import pandas as pd
import matplotlib.pyplot as plt

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
        for time in ["X", "X", "X"]:
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

        tab_control.add(self.tab1, text='Ticket Sales')
        tab_control.add(self.tab2, text='Occupation Rate')
        tab_control.add(self.tab3, text='Screening Rate')

        for tab in (self.tab1, self.tab2, self.tab3):
            main_frame = tk.Frame(tab)
            main_frame.pack(fill="both", expand=True)

            left_frame = tk.Frame(main_frame, width=160, bg="lightgrey")
            left_frame.pack(side="left", fill="y")

            right_frame = tk.Frame(main_frame)
            right_frame.pack(side="right", fill="both", expand=True)

            #Button
            if tab == self.tab1:
                tk.Button(left_frame, text="Logout",width=20,height=2, command=self.logout).pack(pady=3,padx=5)
                tk.Button(left_frame,width=20,height=2, text="PLACEHOLDER", command=self.display_ticket_sales_chart).pack(pady=3,padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2,).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
            elif tab == self.tab2:
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
            elif tab == self.tab3:
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)
                tk.Button(left_frame, text="PLACEHOLDER", width=20, height=2, ).pack(pady=3, padx=5)

    #DEF
    def logout(self):
        self.destroy()

    def display_ticket_sales_chart(self):
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot([1, 2, 3], [4, 5, 6], marker='o', linestyle='-')
        ax.set_title("Monthly Tickets Sold")
        canvas = FigureCanvasTkAgg(fig, master=self.tab1.winfo_children()[0].winfo_children()[1])
        canvas.draw()
        canvas.get_tk_widget().pack(pady=20)

if __name__ == "__main__":
    app=Liemora()
    app.mainloop()

