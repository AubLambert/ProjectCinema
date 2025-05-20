import tkinter as tk
from tkinter import Label, Frame, Button, Toplevel
from PIL import Image, ImageTk
import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "admin",
    password = "quang123",
    database="cinema_management"
)

root = tk.Tk()
root.title("Movie Selection")
root.geometry("1000x700")
root.configure(bg="white")

back_button = Button(root, text="BACK", font=10, width=7, height=1)
back_button.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

grid_frame = Frame(root, bg="white")
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
    r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg",
    r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg",
    r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg",
    r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg",
    r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg",
    r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\Images\Johnwick.jpg"
]

timeslot_window = None
def timeslot_gui(movie_title):
    global timeslot_window
    if timeslot_window is None or not timeslot_window.winfo_exists():
        timeslot_window = Toplevel(root)
        timeslot_window.title(f"Select Timeslot - {movie_title}")
        timeslot_window.geometry("500x400")
        Label(timeslot_window, text=f"Timeslots for '{movie_title}'", font=14).pack(pady=20)
        for time in ["X", "X", "X",  "X"]: #thay đổi timeslot ở đây
            Button(timeslot_window, text=time, width=15).pack(pady=5)
        timeslot_window.transient(root)
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

root.mainloop()

