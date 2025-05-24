import tkinter as tk
from tkinter import messagebox, font, Label, Frame, Button, Toplevel
from PIL import Image, ImageTk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error

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
        bg_image = Image.open(r"D:\Works\BA\Database management\ProjectCinema\python\Images\Cat.jpg").resize((700, 500), Image.LANCZOS)
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
        images = [r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg",
                  r"D:\Works\BA\Database management\ProjectCinema\python\Images\Interstellar.jpg",
                  r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg",
                  r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg",
                  r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg",
                  r"D:\Works\BA\Database management\ProjectCinema\python\Images\Johnwick.jpg"] # Đổi lại path của ảnh

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
        tab_control = ttk.Notebook(self)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        #Style Configuration
        style = ttk.Style(self)
        style.theme_use('default')
        style.layout("TNotebook.Tab", [("Notebook.tab", {"sticky": "nsew","children": [("Notebook.padding", {"sticky": "nsew","children": [("Notebook.label", {"sticky": "nsew"})]})]})])
        style.map("TNotebook.Tab",background=[("selected", "white")],foreground=[("selected", "black")])
        style.configure("TNotebook.Tab",padding=(0, 10),font="bold",background="lightgrey",foreground="black",width=450,anchor="center")

        #tab control
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Ticket Sales')
        tab_control.add(tab2, text='Occupation Rate')
        tab_control.add(tab3, text='Screening Rate')
        tab_control.pack(expand=True, fill='both')

        logout_button = Button(tab1, text="Logout", font="bold", command=self.logout)
        logout_button.pack(pady=10, padx=10, side="left", anchor="sw")

    #def
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

if __name__ == "__main__":
    app=Liemora()
    app.mainloop()

