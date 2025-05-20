import tkinter as tk
from tkinter import Label, Frame, Button

root = tk.Tk()
root.title("Movie Selection")
root.geometry("1000x700")
root.configure(bg="white")

back_button = Button(root, text="BACK", font=(10), width=7, height=1)
back_button.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

grid_frame = Frame(root, bg="white")
grid_frame.place(relx=0.5, rely=0.55, anchor="center")

movie_titles = [
    "John Weed", "Edge of Tomorrow", "Interstellar",
    "Coco", "Parasite", "The Revenant"
]

def timeslot_gui(movie_title):
    timeslot_window = Toplevel(root)
    timeslot_window.title(f"Select Timeslot - {movie_title}")
    timeslot_window.geometry("400x300")
    Label(timeslot_window, text=f"Timeslots for '{movie_title}'", font=("Arial", 14)).pack(pady=20)
    for time in ["10:00 AM", "1:00 PM", "4:00 PM", "7:00 PM"]:
        Button(timeslot_window, text=time, width=15).pack(pady=5)

poster_width = 24
poster_height = 13
horizontal_spacing = 80
vertical_spacing = 60

for index, title in enumerate(movie_titles):
    row = (index // 3) * 2
    col = index % 3

    poster_button = Button(
        grid_frame,
        width=poster_width,
        height=poster_height,
        bg="white",
        relief="solid",
        borderwidth=1,
    )
    poster_button.grid(row=row, column=col, padx=horizontal_spacing, pady=(0, 10))
    poster_button.grid_propagate(False)

    label = Label(grid_frame, text=title, font=(10), bg="white")
    label.grid(row=row + 1, column=col, pady=(0, vertical_spacing))

root.mainloop()

