DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    userID INT(11) UNIQUE NOT NULL AUTO_INCREMENT,
    userName VARCHAR(255) UNIQUE NOT NULL ,
    password VARCHAR(255) NOT NULL,
    firstName VARCHAR(255) NOT NULL,
    lastName VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    dateJoined DATE NOT NULL,
    PRIMARY KEY (userID)
);

INSERT INTO Users (userName, password, firstName, lastName, email, dateJoined) VALUES 
    ('johndoe', 'pbkdf2:sha256:150000$iD5kR8qS$01a43a001a115b0747ed312a66686405225c1658ab8bf57f5a46e94d0393039e', 'John', 'Doe', 'johndoe@gmail.com', '2020-04-04'),
    ('janedoe', 'pbkdf2:sha256:150000$jrbRgQyP$ff64293bbc3e65a67a48a9cb878d38327c5a17f6994b4e55205b5fbd67819257', 'Jane', 'Doe', 'janedoe@gmail.com', '2019-04-04'),
    ('jimdoe', 'pbkdf2:sha256:150000$OlA1Whpp$53a114e19713849f5db98730c6fe70d0bf0b5afa2669a08ed5170f9b9ea95ca7', 'Jim', 'Doe', 'jimdoe@gmail.com', '2018-04-04');

DROP TABLE IF EXISTS Listings;

CREATE TABLE Listings (
    listingID INT(11) UNIQUE NOT NULL AUTO_INCREMENT,
    userID INT(11),
    bidID INT(11),
    make VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    year INT(11) NOT NULL,
    mileage INT(11) NOT NULL,
    reserve INT(11) NOT NULL,
    listDate DATE NOT NULL,
    expirationDate DATE NOT NULL,
    PRIMARY KEY (listingID),
    FOREIGN KEY (userID) REFERENCES Users(userID)
);

INSERT INTO Listings (userID, bidID, make, model, year, mileage, reserve, listDate, expirationDate) VALUES 
    (1, NULL, 'Ford', 'Mustang', 1972, 130000, 100000, '2020-04-04', '2022-06-06'),
    (2, NULL, 'Volvo', 'V70R', 2002, 150000, 110000, '2020-03-04', '2022-05-06'),
    (3, NULL, 'Mercedes', '300SL Gullwing', 1963, 10000, 130000, '2020-02-04', '2022-04-06'),
    (3, NULL, 'Ferrari', 'F40 GTR', 1999, 45783, 1500000, '2020-01-04', '2022-02-03');

DROP TABLE IF EXISTS Bids;

CREATE TABLE Bids (
    bidID INT(11) UNIQUE NOT NULL AUTO_INCREMENT,
    userID INT(11) NOT NULL,
    listingID INT(11) NOT NULL,
    bidAmt INT(11) NOT NULL,
    bidDate DATE NOT NULL,
    PRIMARY KEY (bidID),
    FOREIGN KEY (userID) REFERENCES Users(userID),
    FOREIGN KEY (listingID) REFERENCES Listings(listingID)
);

ALTER TABLE Listings
ADD FOREIGN KEY (bidID) REFERENCES Bids(bidID);

INSERT INTO Bids (userID, listingID, bidAmt, bidDate) VALUES 
    (1, 1, 20000, '2020-04-05'),
    (1, 2, 50000, '2020-03-06'),
    (2, 3, 70000, '2020-02-08'),
    (3, 1, 25000, '2020-04-06');

UPDATE Listings SET bidID = 4 WHERE listingID = 1;
UPDATE Listings SET bidID = 2 WHERE listingID = 2;
UPDATE Listings SET bidID = 3 WHERE listingID = 3;

DROP TABLE IF EXISTS Features;

CREATE TABLE Features (
    featureID INT(11) UNIQUE NOT NULL AUTO_INCREMENT,
    carFeature VARCHAR(255) UNIQUE NOT NULL,
    PRIMARY KEY (featureID)
);

INSERT INTO Features (carFeature) VALUES ('Manual'), ('Electric'), ('Convertible'), ('4WD');

DROP TABLE IF EXISTS Photos;

CREATE TABLE Photos (
    photoID INT(11) UNIQUE NOT NULL AUTO_INCREMENT,
    listingID INT(11) NOT NULL,
    photoPath VARCHAR(255) NOT NULL,
    PRIMARY KEY (photoID),
    FOREIGN KEY (listingID) REFERENCES Listings(listingID)
);

INSERT INTO Photos (listingID, photoPath) VALUES
    (1, 'static/img/test_car_img.jpg'),
    (2, 'static/img/test_car_img.jpg'),
    (3, 'static/img/test_car_img.jpg'),
    (4, 'static/img/test_car_img.jpg');

DROP TABLE IF EXISTS FeaturesListings;

CREATE TABLE FeaturesListings (
    listingID INT(11),
    featureID INT(11),
    PRIMARY KEY (listingID, featureID),
    FOREIGN KEY (listingID) REFERENCES Listings(listingID),
    FOREIGN KEY (featureID) REFERENCES Features(featureID)
);

INSERT INTO FeaturesListings (listingID, featureID) VALUES
    (1, 1), (1, 2),
    (2, 2), (2, 3),
    (3, 1), (3, 3),
    (4, 1), (4, 3);