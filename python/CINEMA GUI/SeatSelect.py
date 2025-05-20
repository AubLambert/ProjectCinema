import tkinter as tk
from tkinter import *
import mysql.connector
from mysql.connector import Error

#root
root = Tk()
root.geometry("1200x700")

#Frames
top_frame = Frame(root, width = 700, height = 100)
top_frame.pack()

#Widget
back_button = Button(root, text="BACK", font=("Arial", 10), width=7, height=1)
back_button.place(x=10, y=10)
screen_label = Label(top_frame, text = "Screen", width = 100)


root.title("SeatManagement")
root.mainloop()