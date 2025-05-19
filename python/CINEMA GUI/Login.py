import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk

root = tk.Tk()
root.title("LIEMORA Cinema Login")
root.geometry("650x450")
root.resizable(True, True)

bg_image = Image.open(r"C:\Users\HACOM\Documents\GitHub\ProjectCinema\python\CINEMA GUI\Cat.jpg")
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

login_button = tk.Button(frame, text="Login", width=10)
login_button.pack(pady=10)

root.mainloop()
