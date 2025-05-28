-- BƯỚC 1: Thêm cột trạng thái ghế vào bảng Seats
ALTER TABLE Seats ADD COLUMN SeatStatus ENUM('Available', 'Booked') DEFAULT 'Available';

-- BƯỚC 2: Trigger tự động cập nhật trạng thái ghế khi đặt vé
DELIMITER //
CREATE TRIGGER update_seat_status_after_booking
AFTER INSERT ON Tickets
FOR EACH ROW
BEGIN
    UPDATE Seats 
    SET SeatStatus = 'Booked' 
    WHERE SeatID = NEW.SeatID;
END//
DELIMITER ;

-- BƯỚC 3: Trigger tự động cập nhật trạng thái ghế khi hủy vé
DELIMITER //
CREATE TRIGGER update_seat_status_after_cancel
AFTER DELETE ON Tickets
FOR EACH ROW
BEGIN
    UPDATE Seats 
    SET SeatStatus = 'Available' 
    WHERE SeatID = OLD.SeatID;
END//
DELIMITER ;

-- BƯỚC 4: Trigger cập nhật khi cập nhật vé (nếu đổi ghế)
DELIMITER //
CREATE TRIGGER update_seat_status_after_update
AFTER UPDATE ON Tickets
FOR EACH ROW
BEGIN
    -- Nếu đổi ghế khác
    IF OLD.SeatID != NEW.SeatID THEN
        -- Ghế cũ chuyển về Available
        UPDATE Seats 
        SET SeatStatus = 'Available' 
        WHERE SeatID = OLD.SeatID;
        
        -- Ghế mới chuyển thành Booked
        UPDATE Seats 
        SET SeatStatus = 'Booked' 
        WHERE SeatID = NEW.SeatID;
    END IF;
END//
DELIMITER ;

-- Event tự động reset ghế sau khi suất chiếu kết thúc
SET GLOBAL event_scheduler = ON;
DELIMITER //
CREATE EVENT clear_expired_seats
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
	UPDATE Seats
	SET SeatStatus = 'Available'
	WHERE SeatID IN (
		SELECT SeatID
		FROM Tickets t
		JOIN Screenings s ON t.ScreeningID = s.ScreeningID
		WHERE TIMESTAMP(s.ScreeningDate, s.ScreeningTime) < NOW()
		);
END //
DELIMITER ;
