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
SELECT s.ScreeningDate, m.MovieTitle, r.RoomName, COUNT(s.MovieID) AS total_screening
FROM screenings s
JOIN movies m ON s.movieID = m.movieID
JOIN cinemarooms r ON s.RoomID = r.RoomID
WHERE s.ScreeningDate = CURDATE()
GROUP BY ScreeningDate, MovieTitle, RoomName;

SELECT * FROM daily_screening;

# Available seats
CREATE OR REPLACE VIEW available_seat AS
SELECT s.ScreeningDate, m.MovieTitle, r.RoomName, r.Capacity, COUNT(t.SeatNumber) AS Booked_seats, r.Capacity - COUNT(t.SeatNumber) AS available_seats
FROM screenings s
JOIN movies m ON s.movieID = m.movieID
JOIN cinemarooms r ON s.RoomID = r.RoomID
JOIN tickets t ON s.ScreeningID = t.ScreeningID
WHERE s.ScreeningDate = CURDATE()
GROUP BY ScreeningDate, MovieTitle, RoomName, r.Capacity;

SELECT * FROM available_seat;

-- Stored procedures
# Ticket booking
DROP PROCEDURE ticket_booking;

DELIMITER //
CREATE PROCEDURE ticket_booking (
	IN cust_name VARCHAR(100), 
	IN cust_phone VARCHAR(100), 
    IN screeningID INT, 
    IN seatnumber VARCHAR(100), 
    OUT result VARCHAR(100))
BEGIN
    DECLARE cust_id INT;
    DECLARE screen_id INT;
    DECLARE slot_exist VARCHAR(100);
    
	proc_end: BEGIN
    -- Validate screening
    SELECT ScreeningID INTO screen_id FROM screenings s WHERE s.ScreeningID = screeningID;
    IF screen_id IS NULL THEN
		SET result = 'Screening does not exist';
        LEAVE proc_end;
    END IF;
    -- Validate seat number
	SELECT t.SeatNumber INTO slot_exist FROM tickets t WHERE t.SeatNumber = seatnumber AND t.ScreeningID = screeningID;
    IF slot_exist IS NOT NULL THEN
		SET result = 'Seat is already taken';
        LEAVE proc_end;
	END IF;
     -- Validate customer
	SELECT c.CustomerID INTO cust_id FROM customers c WHERE c.PhoneNumber = cust_phone;
    IF cust_id IS NULL THEN
		INSERT INTO customers(CustomerName,PhoneNumber) VALUES
        (cust_name, cust_phone);
        SELECT LAST_INSERT_ID() INTO cust_id;
	END IF;
    -- Insert ticket information
    INSERT INTO tickets(CustomerID, ScreeningID, SeatNumber) VALUES (cust_id, screeningID, seatnumber);
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
CREATE PROCEDURE seat_availability (IN screeningID INT, IN seatnumber VARCHAR(100), OUT result VARCHAR(100))
BEGIN
    DECLARE screen_id INT;
    DECLARE slot_exist VARCHAR(100);
-- Validate screening
    SELECT ScreeningID INTO screen_id FROM screenings s WHERE s.ScreeningID = screeningID;
    IF screen_id IS NULL THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Screening does not exist';
    END IF;
    -- Validate seat number
	SELECT t.SeatNumber INTO slot_exist FROM tickets t WHERE t.SeatNumber = seatnumber AND t.ScreeningID = screeningID;
    IF slot_exist IS NOT NULL THEN
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seat is already taken';
	END IF;
    
END //
DELIMITER ;