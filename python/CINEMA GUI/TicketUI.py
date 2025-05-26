import tkinter as tk
from tkinter import *
import mysql.connector
from mysql.connector import Error

class staff_ui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Staff interface")
        self.root.geometry("500x500")
        self.root.configure(bg="white")
        self.staff_interface()
        self.root.mainloop()
    
    def staff_interface(self):
        top_frame = tk.Frame(self.root, bg="white")
        top_frame.place(x=190,y=100)
        option_frame = tk.Frame(self.root, bg="white")
        option_frame.place(x=210,y=200)
        #Welcome
        top_label = tk.Label(top_frame, text="Welcome", font=("bold",20),justify="center")
        top_label.pack(padx=5, pady=5)
        #Options
        search_btn = tk.Button(option_frame, text="Search ticket", font=("bold",10), justify="center",
                               command = "")
        search_btn.pack(pady=10, ipadx=3)
        booking_btn = tk.Button(option_frame, text="Ticket booking", font=("bold", 10), justify="center",
                                command= "")
        booking_btn.pack(pady=10)
if __name__ == "__main__":
    app=staff_ui()
