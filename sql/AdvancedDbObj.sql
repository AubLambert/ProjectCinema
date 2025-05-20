USE cinema_management;

SELECT * FROM cinemarooms;
SELECT * FROM customers;
SELECT * FROM movies;
SELECT * FROM screenings;
SELECT * FROM tickets;
SELECT * FROM seats;
SELECT * FROM payments;

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
DROP PROCEDURE IF EXISTS ticket_booking;

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
	DECLARE EXIT HANDLER FOR SQLEXCEPTION
	BEGIN
		SET result = 'Error: Unable to insert ticket';
	END;
    
        -- Validate screening
        SELECT RoomID INTO room_id FROM Screenings WHERE ScreeningID = screening_id;
        IF room_id IS NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Screening does not exist';
        END IF;

        -- Get SeatID for the given seat code in the correct room
        SELECT SeatID INTO seat_id FROM Seats 
        WHERE RoomID = room_id AND SeatNumber = seat_code;
        IF seat_id IS NULL THEN
            SET result = 'Seat not found in the screening room';
        END IF;

        -- Check if the seat is already booked for the screening
        SELECT COUNT(*) INTO seat_taken FROM Tickets 
        WHERE ScreeningID = screening_id AND SeatID = seat_id;
        IF seat_taken > 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seat already booked';
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
END //
DELIMITER ;

# Testing stored proc
START TRANSACTION;
CALL ticket_booking('Quang', 10101, 1, 'A4', @result);
SELECT @result AS 'Booking status';
ROLLBACK;


# Check seat availability
DROP PROCEDURE IF EXISTS seat_availability;

DELIMITER //
CREATE PROCEDURE seat_availability (
    IN screening_id INT
)
BEGIN
        DECLARE EXIT HANDLER FOR SQLEXCEPTION
		BEGIN
			SET result = 'Error: Unable to check seat availability';
		END; 
         -- Validate screening existence
		IF NOT EXISTS (SELECT 1 FROM Screenings WHERE ScreeningID = screening_id) THEN
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Screening does not exist';
		END IF;
    
        -- Check seat availability
        SELECT SeatID FROM seats s JOIN screenings sc ON s.RoomID = sc.RoomID
        WHERE ScreeningID = screening_id
			AND s.SeatID NOT IN (SELECT t.SeatID FROM tickets t WHERE t.ScreeningID = screening_id);
END //
DELIMITER ;

# Testing stored procedure
CALL seat_availability(1);

-- User defined functions
# Calculate occupancy rate
DROP FUNCTION IF EXISTS calc_OccupancyRate

DELIMITER $$
CREATE FUNCTION calc_OccupancyRate(screen_ID INT)
RETURNS DECIMAL(5,2)
DETERMINISTIC
BEGIN
	DECLARE total_seats INT;
    DECLARE booked_seats INT;
    SET total_seats = (
		SELECT COUNT(se.SeatID) 
        FROM seats se
		WHERE se.RoomID = (
			SELECT s.RoomID FROM screenings s WHERE s.ScreeningID = screen_ID)
		);
	SET booked_seats = (
		SELECT COUNT(t.SeatID)
        FROM tickets t
		WHERE t.ScreeningID = screen_ID
        );
        
	 RETURN (booked_seats/total_seats)*100;
END $$
DELIMITER ;

# Testing UDF
SELECT calc_OccupancyRate(1) AS 'Occupancy Rate (%)'

# Calculate sale revenue per screening
DROP FUNCTION IF EXISTS calc_SaleRevenue

DELIMITER $$
CREATE FUNCTION calc_SaleRevenue(screen_ID INT)
RETURNS FLOAT
DETERMINISTIC
BEGIN
	DECLARE scr_revenue FLOAT;
		SELECT IFNULL(SUM(p.Amount), 0) INTO scr_revenue FROM payments p WHERE p.ScreeningID = screen_ID;
	RETURN scr_revenue;
END $$
DELIMITER ;

# Testing UDF
SELECT calc_SaleRevenue(100) AS 'Total Revenue (VND)';

/* Stored proc for insert fake records
DELIMITER $$

CREATE PROCEDURE seed_demo_data()
BEGIN
    DECLARE i INT DEFAULT 0;
    DECLARE j INT DEFAULT 0;
    DECLARE movie_id INT;
    DECLARE room_id INT;
    DECLARE screen_time TIME;
    DECLARE screen_date DATE;
    DECLARE screening_id INT;
    DECLARE seat_id INT;
    DECLARE customer_id INT;
    DECLARE ticket_id INT;

    -- Temporary holders
    DECLARE movie_count INT;
    DECLARE room_count INT;

    -- Fixed arrays
    CREATE TEMPORARY TABLE temp_movies (id INT);
    CREATE TEMPORARY TABLE temp_rooms (id INT);

    -- Replace with your actual movie and room IDs
    INSERT INTO temp_movies VALUES (1), (3), (4), (10), (13), (7);
    INSERT INTO temp_rooms VALUES (1), (2), (3);

    SET movie_count = (SELECT COUNT(*) FROM temp_movies);
    SET room_count = (SELECT COUNT(*) FROM temp_rooms);

    SET i = 0;
    WHILE i < movie_count DO
        SELECT id INTO movie_id FROM temp_movies LIMIT i,1;
        SET j = 0;

        WHILE j < room_count DO
            SELECT id INTO room_id FROM temp_rooms LIMIT j,1;

            -- Generate a few screenings: today and next 2 days
            SET screen_time = MAKETIME(10 + (j * 2), 0, 0); -- e.g. 10:00, 12:00, 14:00
            SET screen_date = CURDATE() + INTERVAL j DAY;

            -- Insert screening
            INSERT INTO Screenings (MovieID, RoomID, ScreeningDate, ScreeningTime, MovieFormat, Price)
            VALUES (movie_id, room_id, screen_date, screen_time, '2D', 75000);

            SET screening_id = LAST_INSERT_ID();

            -- Create 2 customers, 2 tickets, 2 payments
            INSERT INTO Customers (CustomerName, PhoneNumber)
            VALUES (CONCAT('Demo Cust ', i, j, 'A'), CONCAT('0900', i, j, '1')),
                   (CONCAT('Demo Cust ', i, j, 'B'), CONCAT('0900', i, j, '2'));

            SET customer_id = LAST_INSERT_ID();

            -- Pick 2 seat IDs from the room
            SELECT SeatID INTO seat_id FROM Seats WHERE RoomID = room_id ORDER BY SeatID LIMIT 0,1;

            INSERT INTO Tickets (CustomerID, ScreeningID, SeatID)
            VALUES (customer_id, screening_id, seat_id);

            SET ticket_id = LAST_INSERT_ID();

            INSERT INTO Payments (CustomerID, ScreeningID, TicketID, Amount)
            VALUES (customer_id, screening_id, ticket_id, 75000);

            -- Second customer
            SET customer_id = customer_id + 1;
            SELECT SeatID INTO seat_id FROM Seats WHERE RoomID = room_id ORDER BY SeatID LIMIT 1,1;

            INSERT INTO Tickets (CustomerID, ScreeningID, SeatID)
            VALUES (customer_id, screening_id, seat_id);

            SET ticket_id = LAST_INSERT_ID();

            INSERT INTO Payments (CustomerID, ScreeningID, TicketID, Amount)
            VALUES (customer_id, screening_id, ticket_id, 75000);

            SET j = j + 1;
        END WHILE;

        SET i = i + 1;
    END WHILE;

    DROP TEMPORARY TABLE temp_movies;
    DROP TEMPORARY TABLE temp_rooms;
END$$

DELIMITER ;
*/
