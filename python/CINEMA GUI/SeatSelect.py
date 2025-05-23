import tkinter as tk
from tkinter import *
import mysql.connector
from mysql.connector import Error

class SeatBooking:
    def __init__(self):
        #root
        self.root = tk.Tk()
        self.root.geometry("1200x700")
        self.root.title("Seat booking")
        self.root.resizable("false","false")
        
        self.main_interface()
        self.root.mainloop()
                
        # Initialize data structures
        self.selected_seats = {}
        self.booked_seats = {"A3", "B5", "C2", "D7"}  #Query booked seat
        self.seat_price = 15.00  # Query price per seat
    
    def main_interface(self):
        # Frames
        top_frame = tk.Frame(self.root, bd=3, relief="solid", bg="light grey")
        top_frame.place(x=700,y=30, anchor="n")
        
        bottom_frame = tk.Frame(self.root)
        bottom_frame.place(x=300,y=600)
        
        seat_frame = tk.Frame(self.root)
        seat_frame.place(x=700,y=350, anchor="center")
        
        left_frame = tk.Frame(self.root)
        left_frame.place(x=30,y=300, anchor="w")

        #Main interface
        back_button = tk.Button(self.root, text="BACK", font=("Arial", 10), width=7, height=1, command="")
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
        
        seat_count = 0
        calc_price = 0
        ###Bottom text
        total_seat = tk.Label(bottom_frame, text = f"Total selected seats: {seat_count}", font=("Bold",20))
        total_seat.grid(row=0, column=0)
        
        est_price = tk.Label(bottom_frame, text = f"Est. Price: {calc_price} VND", font=("Bold", 20))
        est_price.grid(row=0, column=1, padx=150)
        
        #Seat layout
        seat_buttons = {}
        ''' thich cai nao hon thi chon
        for col in range(8):
            col_label = tk.Label(seat_frame, text=str(col + 1), font=("Arial", 12, "bold"))
            col_label.grid(row=0, column=col + 1, padx=15, pady=10)
        for row in range(5):
            row_label_right = tk.Label(seat_frame, text=chr(65 + row), font=("Arial", 12, "bold"))
            row_label_right.grid(column=9, padx=(20, 0), pady=20)
        '''
        for row in range(5):
            for col in range(8):
                seat_number = f"{chr(65+row)}{col+1}"  # A1, A2, ...
                seat_button = tk.Button(seat_frame, width=4, height=2, text=f"{seat_number}", relief=tk.RIDGE,bd=1,
                    command=lambda s=seat_number: toggle_seat(s) #seat selection command
                )
                seat_button.grid(row=row+1, column=col+1, padx=15, pady=20)
                seat_buttons[seat_number] = seat_button
                
    def toggle_seat(self):
        # Check if seat is already booked (red)
        if self.seat_buttons[seat_number].cget("bg") == "red":
            return  # Can't select already booked seats
        
        # Check if the seat is already selected
        if seat_id in self.selected_seats:
        # Deselect the seat
            self.seat_buttons[seat_number].config(bg="SystemButtonFace")  # Reset to default color
            del self.selected_seats[seat_number]
        else:
            # Select the seat
            self.seat_buttons[seat_number].config(bg="blue")
            self.selected_seats[seat_number] = True
        # Update total selected seats and price
        self.update_totals()
        
        
if __name__ == "__main__":
    app=SeatBooking()
    app.mainloop()