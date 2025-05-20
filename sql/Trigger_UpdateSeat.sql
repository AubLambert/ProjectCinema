ALTER TABLE Screenings
  ADD COLUMN AvailableSeats INT NOT NULL;

DELIMITER $$

UPDATE Screenings AS s
  JOIN (
    SELECT RoomID, COUNT(*) AS TotalSeats
    FROM Seats
    GROUP BY RoomID
  ) t ON s.RoomID = t.RoomID
SET s.AvailableSeats = t.TotalSeats;

CREATE TRIGGER DecrementSeats
AFTER INSERT ON Tickets
FOR EACH ROW
BEGIN
  UPDATE Screenings
    SET AvailableSeats = AvailableSeats - 1
  WHERE ScreeningID = NEW.ScreeningID;
END$$

CREATE TRIGGER IncrementSeats
AFTER DELETE ON Tickets
FOR EACH ROW
BEGIN
  UPDATE Screenings
    SET AvailableSeats = AvailableSeats + 1
  WHERE ScreeningID = OLD.ScreeningID;
END$$

DELIMITER ;