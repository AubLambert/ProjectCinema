import tkinter as tk
from tkinter import messagebox, font, Label, Frame, Button, Toplevel
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error

timeslot_window = None
mydb = None

def login():
    username = account_entry.get()
    password = password_entry.get()

    try:
        global mydb
        mydb = mysql.connector.connect(
            host='localhost',
            user=username,
            password=password,
            database='cinema_management'
        )

        if mydb.is_connected():
            messagebox.showinfo("Login Success", f"Welcome, {username}")
            root.withdraw()
            if username == "admin":
                open_admin_dashboard()
            else:
                movie_selection_gui()
        else:
            messagebox.showerror("Login Failed", f"Error Occurred")

    except Error as F:
        messagebox.showerror("Login Failed", f"Invalid username or password.\n\n{F}")


root = tk.Tk()
root.title("LIEMORA Cinema Login")
root.geometry("650x450")
root.resizable(True, True)

bg_image = Image.open(r"D:\Works\BA\Database management\ProjectCinema\python\Images\Cat.jpg") #"Copy as path" ảnh CAT trong folder images
bg_image = bg_image.resize((650, 450), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(root, width=600, height=400)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

frame = tk.Frame(canvas, bd=2, relief="solid", padx=25, pady=25)
frame_window = canvas.create_window(325, 225, window=frame)

title_font = font.Font(family="Helvetica", size=14, weight="bold")
title_label = tk.Label(frame, text="LIEMORA Cinema", font=title_font)
title_label.pack(pady=(0, 20))

account_label = tk.Label(frame, text="Account")
account_label.pack()
account_entry = tk.Entry(frame, width=30)
account_entry.pack(pady=5)

password_label = tk.Label(frame, text="Password")
password_label.pack()
password_entry = tk.Entry(frame, show="*", width=30)
password_entry.pack(pady=5)

login_button = tk.Button(frame, text="Login", width=10, command=login)
login_button.pack(pady=10)
root.bind("<Return>", lambda event: login())

def movie_selection_gui():
    global timeslot_window
    root2 = Toplevel(root)
    root2.title("Movie Selection")
    root2.geometry("1000x700")
    root2.configure(bg="white")

    def log_off():
        mydb.close()
        root2.destroy()
        root.deiconify()

    back1_button = Button(root2, text="Logout", font=10, width=7, height=1, command=log_off)
    back1_button.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

    grid_frame = Frame(root2, bg="white")
    grid_frame.place(relx=0.5, rely=0.55, anchor="center")

    movie_titles = [
        "John Weed",
        "Edge of Tomorrow",
        "Interstellar",
        "Coco",
        "Parasite",
        "The Revenant"
    ]

    # Chọn ảnh trong folder images ở python
    movie_images = [
        r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg",
        r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg",
        r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg",
        r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg",
        r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg",
        r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg"
    ]

    timeslot_window = None

    def timeslot_gui(movie_title):
        global timeslot_window
        if timeslot_window is None or not timeslot_window.winfo_exists():
            timeslot_window = Toplevel(root2)
            timeslot_window.title(f"Select Timeslot - {movie_title}")
            timeslot_window.geometry("500x400")
            Label(timeslot_window, text=f"Timeslots for '{movie_title}'", font=14).pack(pady=20)
            for time in ["X", "X", "X", "X"]:  # thay đổi timeslot ở đây
                Button(timeslot_window, text=time, width=15).pack(pady=5)
            timeslot_window.transient(root2)
            timeslot_window.grab_set()

    poster_width = 180
    poster_height = 230
    horizontal_spacing = 50
    vertical_spacing = 25

    for index, title in enumerate(movie_titles):
        row = (index // 3) * 2
        col = index % 3

        img = Image.open(movie_images[index])
        img = img.resize((poster_width, poster_height))
        img = ImageTk.PhotoImage(img)

        poster_button = Button(
            grid_frame,
            width=poster_width,
            height=poster_height,
            bg="white",
            relief="solid",
            borderwidth=1,
            command=lambda t=title: timeslot_gui(t)
        )
        poster_button.image = img
        poster_button.grid(row=row, column=col, padx=horizontal_spacing, pady=(0, 10))
        poster_button.grid_propagate(False)
        poster_button.config(image=img)

        label = Label(grid_frame, text=title, font=10, bg="white")
        label.grid(row=row + 1, column=col, pady=(0, vertical_spacing))
def open_admin_dashboard():
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Dashboard")
    admin_window.geometry("1000x700")
    admin_window.configure(bg="white")
root.mainloop()

