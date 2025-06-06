import tkinter as tk
from tkinter import *
import mysql.connector
from mysql.connector import Error
from Payment import CustomerFormApp

class SeatBooking:
    def __init__(self, parent, db_connection, screening_id, room_name, seat_price):
        #root
        self.parent = parent
        self.db = db_connection
        self.screening_id = screening_id
        self.room_name = room_name
        self.seat_price = seat_price
        
        self.root = tk.Tk()
        self.root.geometry("1200x700")
        self.root.title("Seat booking")
        self.root.resizable(False, False)
        
        # Initialize data structures
        self.selected_seats = {}
        self.booked_seats = set()  #Query booked seat
        self.room_id = self.room_name #Catch screenid from previous tab (query room id from screen id)
        
        self.query_booked_seats()
        self.main_interface()
        self.root.mainloop()
        
    def query_booked_seats(self):
        cursor = self.db.cursor()
        query = """
            SELECT SeatNumber FROM Tickets
            WHERE ScreeningID = %s
        """
        cursor.execute(query, (self.screening_id,))
        results = cursor.fetchall()
        self.booked_seats = set(row[0] for row in results)
        cursor.close()

        
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
        #TODO: back command
        back_button = tk.Button(self.root, text="BACK", font=("Arial", 10), width=7, height=1, command="")
        back_button.place(x=30, y=30)
        
        # Continue button (initially disabled)
        self.continue_button = tk.Button(self.root, text="Payment", 
                                         font=("bold,14"), 
                                         bg="#4CAF50", fg="white",
                                         width=10, height=1,
                                         state="disabled",
                                         command= self.go_to_payment()) #Transition to payment screen #TODO: continue command
        self.continue_button.place(x=1050,y=350)
        ###Screen label
        screen_label = tk.Label(top_frame, text = "Screen", width=30, font = ("Bold",30), justify = "center", bg = "light grey")
        screen_label.pack(padx=10, pady=10, anchor=tk.CENTER)
        
        ###CinemaRoom label
        room_label = tk.Label(tleft_frame, text = f"{self.room_id}", width = 20, font = ("Bold"), justify = "left")
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
    
    def go_to_payment(self):
        self.root.destroy()
#TODO        
CustomerFormApp(
        screening_id=self.screening_id,
        selected_seats=list(self.selected_seats.keys()),
        seat_price=self.seat_price,
        db_connection=self.db
 )
          
       
if __name__ == "__main__":
    app=SeatBooking()
