USE cinema_management;

SELECT * FROM cinemarooms;
SELECT * FROM customers;
SELECT * FROM movies;
SELECT * FROM screenings;
SELECT * FROM tickets;


-- Index
CREATE INDEX idx_title
ON movies(MovieTitle);

CREATE INDEX idx_schedule
ON screenings(ScreeningDate);

-- Views
# Summaries of daily screening
CREATE OR REPLACE VIEW daily_screening AS
SELECT 
  s.ScreeningDate AS 'Date',
  m.MovieTitle AS 'Movie title',
  r.RoomName AS 'Room',
  s.ScreeningTime AS 'Time',
  COUNT(DISTINCT se.SeatID) AS 'Total seats',
  COUNT(DISTINCT t.SeatID) AS 'Booked seats',
  COUNT(DISTINCT se.SeatID) - COUNT(DISTINCT t.SeatID) AS 'Available seats'
FROM Screenings s
JOIN Movies m ON s.MovieID = m.MovieID
JOIN CinemaRooms r ON s.RoomID = r.RoomID
JOIN Seats se ON se.RoomID = r.RoomID
LEFT JOIN Tickets t 
  ON t.ScreeningID = s.ScreeningID AND t.SeatID = se.SeatID
WHERE s.ScreeningDate = '2025-05-11' -- Replace with desired date
GROUP BY s.ScreeningID, s.ScreeningDate, m.MovieTitle, r.RoomName, s.ScreeningTime;

-- View usage:
SELECT * FROM daily_screening;

# Available seats
CREATE OR REPLACE VIEW available_seat AS
SELECT s.ScreeningDate AS 'Date', m.MovieTitle AS 'Movie title', r.RoomName AS 'Room name', COUNT(t.SeatID) AS 'Booked seats', COUNT(se.SeatID) - COUNT(t.SeatID) AS 'Available seats'
FROM Screenings s
JOIN Movies m ON s.MovieID = m.MovieID
JOIN CinemaRooms r ON s.RoomID = r.RoomID
JOIN Seats se ON se.RoomID = r.RoomID
LEFT JOIN Tickets t 
  ON t.ScreeningID = s.ScreeningID AND t.SeatID = se.SeatID
WHERE s.ScreeningDate = '2025-05-11' -- replace any date you want
GROUP BY ScreeningDate, MovieTitle, RoomName;

SELECT * FROM available_seat;

-- Stored procedures
# Ticket booking
DROP PROCEDURE ticket_booking;

DELIMITER //
CREATE PROCEDURE ticket_booking (
	IN cust_name VARCHAR(100), 
	IN cust_phone VARCHAR(100), 
    IN screening_id INT, 
    IN seat_code VARCHAR(100), 
    OUT result VARCHAR(100)
)
BEGIN
    DECLARE cust_id INT;
    DECLARE room_id INT;
    DECLARE seat_id INT;
    DECLARE seat_taken INT;

    proc_end: BEGIN
        -- Validate screening
        SELECT RoomID INTO room_id FROM Screenings WHERE ScreeningID = screening_id;
        IF room_id IS NULL THEN
            SET result = 'Screening does not exist';
            LEAVE proc_end;
        END IF;

        -- Get SeatID for the given seat code in the correct room
        SELECT SeatID INTO seat_id FROM Seats 
        WHERE RoomID = room_id AND SeatNumber = seat_code;
        IF seat_id IS NULL THEN
            SET result = 'Seat not found in the screening room';
            LEAVE proc_end;
        END IF;

        -- Check if the seat is already booked for the screening
        SELECT COUNT(*) INTO seat_taken FROM Tickets 
        WHERE ScreeningID = screening_id AND SeatID = seat_id;
        IF seat_taken > 0 THEN
            SET result = 'Seat is already taken';
            LEAVE proc_end;
        END IF;

        -- Check if customer exists
        SELECT CustomerID INTO cust_id FROM Customers 
        WHERE PhoneNumber = cust_phone;
        IF cust_id IS NULL THEN
            INSERT INTO Customers (CustomerName, PhoneNumber) 
            VALUES (cust_name, cust_phone);
            SET cust_id = LAST_INSERT_ID();
        END IF;

        -- Insert the ticket
        INSERT INTO Tickets (CustomerID, ScreeningID, SeatID) 
        VALUES (cust_id, screening_id, seat_id);
        
        SET result = 'Ticket booked successfully';
    END proc_end;
END //
DELIMITER ;

# Testing stored proc
START TRANSACTION;
CALL ticket_booking('Quang', 10101, 1, 'A4', @result);
SELECT @result AS 'Booking status';
ROLLBACK;


# Check seat availability
DROP PROCEDURE seat_availability;

DELIMITER //
CREATE PROCEDURE seat_availability (
    IN screening_id INT, 
    IN seat_code VARCHAR(100), 
    OUT result VARCHAR(100)
)
BEGIN
    DECLARE room_id INT;
    DECLARE seat_id INT;
    DECLARE seat_taken INT;
    proc_check: BEGIN
        -- Validate screening
        SELECT RoomID INTO room_id FROM Screenings 
        WHERE ScreeningID = screening_id;
        
        IF room_id IS NULL THEN
            SET result = 'Screening does not exist';
            LEAVE proc_check;
        END IF;

        -- Validate seat number
        SELECT SeatID INTO seat_id FROM Seats 
        WHERE RoomID = room_id AND SeatNumber = seat_code;
        
        IF seat_id IS NULL THEN
            SET result = 'Seat not found in the screening room';
            LEAVE proc_check;
        END IF;

        -- Check seat availability
        SELECT COUNT(*) INTO seat_taken FROM Tickets 
        WHERE ScreeningID = screening_id AND SeatID = seat_id;
        
        IF seat_taken > 0 THEN
            SET result = 'Seat is already taken';
        ELSE
            SET result = 'Seat is available';
        END IF;
    END proc_check;
END //
DELIMITER ;

# Testing stored procedure
CALL seat_availability(3, 'B2', @result);
SELECT @result;