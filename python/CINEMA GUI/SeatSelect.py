import tkinter as tk
from tkinter import *
import mysql.connector
from mysql.connector import Error

#root
root = tk.Tk()
root.geometry("1200x700")
root.title("Seat booking")

# Frames (converted to .pack())
top_frame = tk.Frame(root, bd=3, relief="solid", bg="light grey")
top_frame.pack(padx=(300, 100), pady=30, fill="both")

seat_frame = tk.Frame(root)
seat_frame.pack(side="right", padx=(0,165), pady= 100, fill="both", expand="true")

left_frame = tk.Frame(root)
left_frame.pack(side="left", padx=80, pady=100, fill="both", expand="true")

bottom_frame = tk.Frame(root)
bottom_frame.pack(side="bottom", fill="both", expand="true")

#Main interface
back_button = tk.Button(root, text="BACK", font=("Arial", 10), width=7, height=1, command="")
back_button.place(x=30, y=30)
###Screen label
screen_label = tk.Label(top_frame, text = "Screen", width=30, font = ("Bold",30), justify = "center", bg = "light grey")
screen_label.pack(padx=10, pady=10, anchor=tk.CENTER, fill="both", expand="True")

###Legends
available_seat = tk.Frame(left_frame, width=40, height=40, bg= "white", relief=tk.RIDGE, bd=1)
available_seat.grid(row = 0, column=0)

available_label = tk.Label(left_frame, text = "Available seat", font = 10)
available_label.grid(row= 0, column=1, padx=10, pady=10, sticky='w')

selected_seat = tk.Frame(left_frame, width=40, height=40, bg= "blue", relief=tk.RIDGE, bd=1)
selected_seat.grid(row = 1, column=0)

selected_label = tk.Label(left_frame, text = "Selected seat", font = 10)
selected_label.grid(row= 1, column=1, padx=10, pady=10, sticky='w')

booked_seat = tk.Frame(left_frame, width=40, height=40, bg= "red", relief=tk.RIDGE, bd=1)
booked_seat.grid(row = 2, column=0)

booked_label = tk.Label(left_frame, text = "Booked seat", font = 10)
booked_label.grid(row= 2, column=1, padx=10, pady=10, sticky='w')

###Bottom text
total_seat = tk.Label()

#Seat layout
seat_buttons = {}
for row in range(5):
    for col in range(8):
        seat_id = f"{chr(65+row)}{col+1}"  # A1, A2, ...
        seat_button = tk.Button(seat_frame, width=4, height=2,relief=tk.RIDGE,bd=1,
            command=lambda s=seat_id: toggle_seat(s) #seat selection command
        )
        seat_button.grid(row=row, column=col, padx=10, pady=10)
        seat_buttons[seat_id] = seat_button
        
def toggle_seat(self):
    # Check if seat is already booked (red)
    if self.seat_buttons[seat_id].cget("bg") == "red":
        return  # Can't select already booked seats
    
    # Check if the seat is already selected
    if seat_id in self.selected_seats:
    # Deselect the seat
        self.seat_buttons[seat_id].config(bg="SystemButtonFace")  # Reset to default color
        del self.selected_seats[seat_id]
    else:
        # Select the seat
        self.seat_buttons[seat_id].config(bg="blue")
        self.selected_seats[seat_id] = True
    # Update total selected seats and price
    self.update_totals()
    
    
root.title("Seat Management")
root.mainloop()