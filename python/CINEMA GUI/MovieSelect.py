import tkinter as tk
from tkinter import Label, Frame, Button, Toplevel, ttk
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="quang123",
    database="cinema_management"
)

# ====== SETUP WINDOW ======
root = tk.Tk()
root.title("Movie Selection")
root.geometry("1000x700")
root.configure(bg="white")

# ====== BACK BUTTON ======
back_button = Button(root, text="BACK", font=10, width=7, height=1)
back_button.grid(row=0, column=0, sticky="nw", padx=20, pady=20)

# ====== MOVIE DATA ======
movie_titles = [
    "John Wick",
    "Edge of Tomorrow",
    "Interstellar",
    "Coco",
    "Parasite",
    "The Revenant"
]

movie_images = [
    r"C:\Users\Admin\Downloads\MySQL\Github\ProjectCinema\python\Images\Johnwick.jpg",
    r"C:\Users\Admin\Downloads\MySQL\Github\ProjectCinema\python\Images\EdgeOfTomorrow.jpg",
    r"C:\Users\Admin\Downloads\MySQL\Github\ProjectCinema\python\Images\Interstellar.jpg",
    r"C:\Users\Admin\Downloads\MySQL\Github\ProjectCinema\python\Images\Coco.jpg",
    r"C:\Users\Admin\Downloads\MySQL\Github\ProjectCinema\python\Images\Parasite.jpg",
    r"C:\Users\Admin\Downloads\MySQL\Github\ProjectCinema\python\Images\TheRevenant.jpg"
]

movie_image_map = dict(zip(movie_titles, movie_images))

# ====== MAIN POSTER GRID ======
grid_frame = Frame(root, bg="white")
grid_frame.place(relx=0.5, rely=0.55, anchor="center")

poster_width = 180
poster_height = 230
horizontal_spacing = 50
vertical_spacing = 25

def timeslot_gui(movie_title):
    global timeslot_window
    if 'timeslot_window' in globals() and timeslot_window.winfo_exists():
        timeslot_window.destroy()

    timeslot_window = Toplevel(root)
    timeslot_window.title(f"Select Timeslot - {movie_title}")

    # Center popup (2/3 screen)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    win_width = int(screen_width * 2 / 3)
    win_height = int(screen_height * 2 / 3)
    x_pos = int((screen_width - win_width) / 2)
    y_pos = int((screen_height - win_height) / 2)
    timeslot_window.geometry(f"{win_width}x{win_height}+{x_pos}+{y_pos}")
    timeslot_window.configure(bg="white")

    # BACK button
    Button(timeslot_window, text="BACK", command=timeslot_window.destroy).place(x=15, y=15)

    # Poster
    try:
        img_path = movie_image_map[movie_title]
        img = Image.open(img_path)
        img = img.resize((200, 280))
        poster_img = ImageTk.PhotoImage(img)

        poster = Label(timeslot_window, image=poster_img, relief="solid", borderwidth=1)
        poster.image = poster_img
        poster.place(x=40, y=80)
    except Exception as e:
        poster = Label(timeslot_window, text="No\nImage", width=20, height=10, bg="lightgray", relief="solid")
        poster.place(x=40, y=80)

    # Title
    Label(
        timeslot_window,
        text=f"Movie schedule for '{movie_title}'",
        font=("Helvetica", 18, "bold"),
        bg="white"
    ).place(x=280, y=90)

    # Table frame
    table_frame = Frame(timeslot_window, bg="white")
    table_frame.place(x=270, y=150, width=win_width - 320, height=win_height - 230)

    columns = ("Date", "Time", "Format", "Room")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Helvetica", 13, "bold"))
    style.configure("Treeview", font=("Helvetica", 12), rowheight=36)

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)

    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Import database:
    now = datetime.now()
    cursor = mydb.cursor()

    query = """
        SELECT s.ScreeningDate, s.ScreeningTime, s.MovieFormat, r.RoomName
        FROM Screenings s
        JOIN Movies m ON s.MovieID = m.MovieID
        JOIN CinemaRooms r ON s.RoomID = r.RoomID
        WHERE m.MovieTitle = %s
          AND s.ScreeningDate >= NOW()
        ORDER BY s.ScreeningDate, s.ScreeningTime
    """
    cursor.execute(query, (movie_title,))
    results = cursor.fetchall()

    for row in results:
        screening_date = row[0].strftime("%Y-%m-%d")
        screening_time = f"{row[1].seconds // 3600:02}:{(row[1].seconds // 60) % 60:02}"
        tree.insert("", "end", values=(screening_date, screening_time, row[2], row[3]))

    cursor.close()

    # SELECT Button
    Button(timeslot_window, text="SELECT", font=("Helvetica", 12), width=14).place(
        relx=0.5, rely=0.92, anchor="center"
    )

    timeslot_window.transient(root)
    timeslot_window.grab_set()


# ====== POSTER GRID GENERATOR ======
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

    label = Label(grid_frame, text=title, font=("Helvetica", 12), bg="white")
    label.grid(row=row + 1, column=col, pady=(0, vertical_spacing))

root.mainloop()
