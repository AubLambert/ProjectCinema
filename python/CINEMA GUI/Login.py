import tkinter as tk
from tkinter import messagebox
from tkinter import font
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error

class Liemora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LIEMORA Cinema Login")
        self.geometry("700x500")
        self.resizable(False, False)
        self.mydb = None
        self.timeslot_window = None
        self.build_login_ui()
        self.bg_photo = None
        self.account_entry = None
        self.password_entry = None

    def build_login_ui(self):
        bg_image = Image.open(r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Cat.jpg").resize((700, 500),
                                                                                                             Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)  # Store directly to instance attribute

        canvas = tk.Canvas(self, width=650, height=450)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

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
                    AdminGUI(self)
                else:
                    MovieSelection(self, username)
            else:
                messagebox.showerror("Login Failed", "Error Occurred")

        except Error as e:
            messagebox.showerror("Login Failed", f"Invalid username or password.\n\n{e}")
app=Liemora()
app.mainloop()
