import tkinter as tk
from SeatSelect import SeatBooking
from tkinter import messagebox
from tkinter import Label, Frame, Button, Toplevel, ttk
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import mysql.connector
import os
base_dir = os.path.dirname(__file__)

mydb = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="quang123",
    database="cinema_management"
)

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
        cursor = self.main.mydb.cursor()
        cursor.execute("SELECT RoomID FROM CinemaRooms WHERE RoomName = %s", (room_name,))
        room_result = cursor.fetchone()
        cursor.close()

        if not room_result:
            messagebox.showerror("Error", "Room not found.")
            return

        room_id = room_result[0]

        # Gọi GUI SeatBooking và truyền dữ liệu
        self.withdraw()
        self.timeslot_window.destroy()
        SeatBooking(self, self.main.mydb, movie_title, screening_date, screening_time, room_id)
if __name__ == "__main__":
    app=Movie()
