CREATE TABLE users (
    userID INT(11) NOT NULL AUTO_INCREMENT,
    userName VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstName VARCHAR(255) NOT NULL,
    lastName VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    dateJoined DATE NOT NULL,
    PRIMARY KEY (userID)
);

INSERT INTO users (userName, password, firstName, lastName, email, dateJoined) VALUES 
    ('johndoe', 'password1', 'John', 'Doe', 'johndoe@gmail.com', '2020-04-04'),
    ('janedoe', 'password2', 'Jane', 'Doe', 'janedoe@gmail.com', '2019-04-04'),
    ('jimdoe', 'password3', 'Jim', 'Doe', 'jimdoe@gmail.com', '2018-04-04');

CREATE TABLE listings (
    listingID INT(11) NOT NULL AUTO_INCREMENT,
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
    FOREIGN KEY (userID) REFERENCES users(userID)
);

INSERT INTO listings (userID, make, model, year, mileage, reserve, listDate, expirationDate) VALUES 
    (1, 'Ford', 'Mustang', 1972, 130000, 100000, '2020-04-04', '2020-06-06'),
    (2, 'Volvo', 'V70R', 2002, 150000, 110000, '2020-03-04', '2020-05-06'),
    (3, 'Mercedes', '300SL Gullwing', 1963, 10000, 130000, '2020-02-04', '2020-04-06'),
    (3, 'Ferrari', 'F40 GTR', 1999, 45783, 1500000, '2020-01-04', '2020-02-03');

CREATE TABLE bids (
    bidID INT(11) NOT NULL AUTO_INCREMENT,
    userID INT(11) NOT NULL,
    listingID INT(11) NOT NULL,
    bidAmt INT(11) NOT NULL,
    bidDate DATE NOT NULL,
    PRIMARY KEY (bidID),
    FOREIGN KEY (userID) REFERENCES users(userID),
    FOREIGN KEY (listingID) REFERENCES listings(listingID)
);

ALTER TABLE listings
ADD FOREIGN KEY (bidID) REFERENCES bids(bidID);

INSERT INTO bids (userID, listingID, bidAmt, bidDate) VALUES 
    (1, 1, 20000, '2020-04-05'),
    (1, 2, 50000, '2020-03-06'),
    (2, 3, 70000, '2020-02-08'),
    (3, 1, 25000, '2020-04-06');

UPDATE listings SET bidID = 4 WHERE listingID = 1;
UPDATE listings SET bidID = 2 WHERE listingID = 2;
UPDATE listings SET bidID = 3 WHERE listingID = 3;

CREATE TABLE features (
    featureID INT(11) NOT NULL AUTO_INCREMENT,
    carFeature VARCHAR(255) UNIQUE NOT NULL,
    PRIMARY KEY (featureID)
);

INSERT INTO features (carFeature) VALUES ('Manual'), ('Electric'), ('Convertible'), ('4WD');

CREATE TABLE photos (
    photoID INT(11) NOT NULL AUTO_INCREMENT,
    listingID INT(11) NOT NULL,
    photoPath VARCHAR(255) NOT NULL,
    PRIMARY KEY (photoID),
    FOREIGN KEY (listingID) REFERENCES listings(listingID)
);

CREATE TABLE FeaturesListings (
    listingID INT(11),
    featureID INT(11),
    PRIMARY KEY (listingID, featureID),
    FOREIGN KEY (listingID) REFERENCES listings(listingID),
    FOREIGN KEY (featureID) REFERENCES features(featureID)
);

INSERT INTO FeaturesListings (listingID, featureID) VALUES
    (1, 1), (1, 2),
    (2, 2), (2, 3),
    (3, 1), (3, 3),
    (4, 1), (4, 3);