-- Import script

-- Movies
INSERT INTO Movies (Genre, MovieTitle, DurationMinutes) VALUES
('Action', 'Edge of Tomorrow', 113),
('Drama', 'The Shawshank Redemption', 142),
('Sci-Fi', 'Interstellar', 169),
('Action', 'John Wick', 101),
('Comedy', 'The Grand Budapest Hotel', 99),
('Drama', 'A Beautiful Mind', 135);

-- Cinema Rooms
INSERT INTO CinemaRooms (RoomName, Capacity) VALUES
('Screen 1', 150),
('Screen 2', 120),
('Screen 3', 200),
('Screen 4', 180),
('Screen 5', 160),
('Screen 6', 140);

-- Customers
INSERT INTO Customers (CustomerName, DOB, PhoneNumber) VALUES
('Alice Johnson', '1990-05-14', 1234567890),
('Bob Smith', '1985-09-23', 2345678901),
('Charlie Lee', '2000-01-11', 3456789012),
('Diana Wang', '1992-07-30', 4567890123),
('Edward Kim', '1999-03-22', 5678901234),
('Fiona Brown', '1995-12-01', 6789012345),
('George Davis', '1988-06-18', 7890123456),
('Hannah Wilson', '1993-08-05', 8901234567),
('Ian Taylor', '2002-10-20', 9012345678),
('Julia Martinez', '1997-11-09', 1122334455);

-- Screenings
INSERT INTO Screenings (MovieID, RoomID, ScreeningDate, ScreeningTime) VALUES
(1, 1, '2025-05-10', '18:00'), -- Edge of Tomorrow in Screen 1
(2, 2, '2025-05-10', '20:30'), -- Shawshank in Screen 2
(3, 3, '2025-05-11', '17:15'), -- Interstellar in Screen 3
(4, 4, '2025-05-11', '19:00'), -- John Wick in Screen 4
(1, 5, '2025-05-12', '18:30'), -- Edge again in Screen 5
(5, 6, '2025-05-12', '20:00'), -- Grand Budapest in Screen 6
(6, 1, '2025-05-13', '17:00'), -- A Beautiful Mind in Screen 1
(2, 2, '2025-05-13', '19:30'), -- Shawshank again in Screen 2
(4, 3, '2025-05-14', '16:00'), -- John Wick again in Screen 3
(3, 4, '2025-05-14', '21:00'); -- Interstellar again in Screen 4

-- Tickets
INSERT INTO Tickets (CustomerID, ScreeningID, SeatNumber) VALUES
(1, 1, 'A1'),
(2, 1, 'A2'),
(3, 2, 'B5'),
(4, 3, 'C3'),
(5, 4, 'D6'),
(6, 5, 'E2'),
(7, 6, 'F1'),
(8, 7, 'G8'),
(9, 8, 'H3'),
(10, 9, 'I4');

