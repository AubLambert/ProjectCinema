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
        
        # Initialize data structures
        self.selected_seats = {}
        self.booked_seats = {"A3", "B5", "C2", "D7"}  #Query booked seat, example
        self.seat_price = 75000  # Query price per seat, example
        self.room_id = 1 #Catch screenid from previous tab (query room id from screen id)
        
        self.main_interface()
        self.root.mainloop()
        
    def main_interface(self):
        # Frames
        top_frame = tk.Frame(self.root, bd=3, relief="solid", bg="light grey")
        top_frame.place(x=700,y=30, anchor="n")
        
        bottom_frame = tk.Frame(self.root)
        bottom_frame.place(x=300,y=600)
        
        seat_frame = tk.Frame(self.root)
        seat_frame.place(x=700,y=350, anchor="center")
        
        tleft_frame = tk.Frame(self.root, bd = 1, relief= "solid")
        tleft_frame.place(x=100, y = 150)
        
        left_frame = tk.Frame(self.root)
        left_frame.place(x=100,y=350, anchor="w")
        
        #Main interface
        back_button = tk.Button(self.root, text="BACK", font=("Arial", 10), width=7, height=1, command="")
        back_button.place(x=30, y=30)
        
        # Continue button (initially disabled)
        self.continue_button = tk.Button(self.root, text="Payment", 
                                         font=("bold,14"), 
                                         bg="#4CAF50", fg="white",
                                         width=10, height=1,
                                         state="disabled",
                                         command="") #Transition to payment screen
        self.continue_button.place(x=1050,y=350)
        ###Screen label
        screen_label = tk.Label(top_frame, text = "Screen", width=30, font = ("Bold",30), justify = "center", bg = "light grey")
        screen_label.pack(padx=10, pady=10, anchor=tk.CENTER)
        
        ###CinemaRoom label
        room_label = tk.Label(tleft_frame, text = f"Screen {self.room_id}", width = 20, font = ("Bold"), justify = "left")
        room_label.pack(pady=(10,10))
        
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
        self.total_seat = tk.Label(bottom_frame, text = "Total selected seats: 0", font=("Bold",20))
        self.total_seat.grid(row=0, column=0)
        
        self.est_price = tk.Label(bottom_frame, text = "Est. Price: 0 VND", font=("Bold", 20))
        self.est_price.grid(row=0, column=1, padx=150)
        
        #Seat layout
        self.seat_buttons = {}
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
                
                # Determine initial color
                if seat_number in self.booked_seats:
                    bg_color = "red"
                    fg_color= "white"
                    state = "disabled"
                else:
                    bg_color = "white"
                    fg_color = "black"
                    state = "normal"
                  
                seat_button = tk.Button(seat_frame, width=4, height=2, text=f"{seat_number}", relief=tk.RIDGE,bd=1,
                    fg=fg_color, state=state, bg = bg_color, command=lambda s=seat_number: self.toggle_seat(s) #seat selection command
                )
                seat_button.grid(row=row+1, column=col+1, padx=15, pady=20)
                self.seat_buttons[seat_number] = seat_button
                
    def toggle_seat(self,seat_number):
        # Check if seat is already booked (red)
        if self.seat_buttons[seat_number].cget("bg") == "red":
            return  # Can't select already booked seats
        
        # Check if the seat is already selected
        if seat_number in self.selected_seats:
        # Deselect the seat
            self.seat_buttons[seat_number].config(bg="white", fg = "black")  # Reset to default color
            del self.selected_seats[seat_number]
        else:
            # Select the seat
            self.seat_buttons[seat_number].config(bg="blue", fg = "white")
            self.selected_seats[seat_number] = True
        # Update total selected seats and price
        self.update_totals()
    
    def update_totals(self):
       total_selected = len(self.selected_seats)
       total_price = total_selected * self.seat_price
       
       self.total_seat.config(text=f"Total selected seats: {total_selected}")
       self.est_price.config(text=f"Est. Price: {total_price} VND")
        
       if total_selected > 0:
           self.continue_button.config(state="normal")
       else:
           self.continue_button.config(state="disabled")
           
           
       
if __name__ == "__main__":
    app=SeatBooking()
