-- Generate script:
CREATE DATABASE cinema_management;

USE cinema_management;

CREATE TABLE Movies
(
  MovieID INT NOT NULL AUTO_INCREMENT,
  Genre VARCHAR(100) NOT NULL,
  MovieTitle VARCHAR(100) NOT NULL,
  DurationMinutes NUMERIC NOT NULL,
  PRIMARY KEY (MovieID)
);

CREATE TABLE CinemaRooms
(
  RoomID INT NOT NULL AUTO_INCREMENT,
  RoomName VARCHAR(100) NOT NULL,
  Capacity INT NOT NULL,
  PRIMARY KEY (RoomID)
);

CREATE TABLE Customers
(
  CustomerID INT NOT NULL AUTO_INCREMENT,
  CustomerName VARCHAR(100) NOT NULL,
  DOB DATE NULL,
  PhoneNumber VARCHAR(100) NOT NULL UNIQUE,
  PRIMARY KEY (CustomerID)
);

CREATE TABLE Screenings
(
  ScreeningID INT NOT NULL AUTO_INCREMENT,
  MovieID INT NOT NULL,
  RoomID INT NOT NULL,
  ScreeningDate DATE NOT NULL,
  ScreeningTime TIME NOT NULL,
  PRIMARY KEY (ScreeningID),
  FOREIGN KEY (MovieID) REFERENCES Movies(MovieID),
  FOREIGN KEY (RoomID) REFERENCES CinemaRooms(RoomID)
);

CREATE TABLE Tickets
(
  TicketID INT NOT NULL AUTO_INCREMENT,
  CustomerID INT NOT NULL,
  ScreeningID INT NOT NULL,
  SeatNumber VARCHAR(100) NOT NULL,
  PRIMARY KEY (TicketID),
  FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
  FOREIGN KEY (ScreeningID) REFERENCES Screenings(ScreeningID)
);
