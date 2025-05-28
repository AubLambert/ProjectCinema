import tkinter as tk
from tkinter import *
import mysql.connector
from mysql.connector import Error

class staff_ui(tk.Toplevel):
    def __init__(self, main, username):
        super().__init__(main)
        self.main=main
        self.username=username
        self.title("Staff interface")
        self.geometry("500x500")
        self.configure(bg="white")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.staff_interface()
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
    def staff_interface(self):
        tk.Button(self, text="Logout", font=10, width=7, command=self.logout).grid(row=0, column=0, sticky="nw", padx=20, pady=20)
        top_frame = tk.Frame(self, bg="white")
        top_frame.place(x=190,y=100)
        option_frame = tk.Frame(self, bg="white")
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
