SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS fighters;
DROP TABLE IF EXISTS fights;
DROP TABLE IF EXISTS prizes;
DROP TABLE IF EXISTS weapons;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `Prizes`(
`prizeID` int(11) NOT NULL AUTO_INCREMENT,
`prizeType` varchar(255) NOT NULL,
PRIMARY KEY (`prizeID`),
UNIQUE(`prizeID`)
);

CREATE TABLE `Weapons`(
`weaponID` int(11) NOT NULL AUTO_INCREMENT,
`weaponName` varchar(255) NOT NULL,
`weaponType` varchar(255) NOT NULL,
`ranged` BOOL NOT NULL,
PRIMARY KEY (`weaponID`),
UNIQUE(`weaponID`)
);

CREATE TABLE `Fighters` (
`fighterID` int(11) NOT NULL AUTO_INCREMENT,
`fighterName` varchar(255) NOT NULL,
`weapon` int(11) DEFAULT NULL,
PRIMARY KEY (`fighterID`),
FOREIGN KEY (`weapon`) REFERENCES `Weapons`(`weaponID`),
UNIQUE(`fighterID`)
);

CREATE TABLE `Fights` (
`fightID` int(11) NOT NULL AUTO_INCREMENT,
`fightDate` date NOT NULL,
`fighter1` int(11),
`fighter2` int(11), 
`fighter1Won` BOOL DEFAULT FALSE,
`fighter2Won` BOOL DEFAULT FALSE,
PRIMARY KEY (`fightID`),
FOREIGN KEY (`fighter1`) REFERENCES `Fighters`(`fighterID`),
FOREIGN KEY (`fighter2`) REFERENCES `Fighters`(`fighterID`),
UNIQUE(`fightID`)
);

CREATE TABLE `PrizesWon` (
`prizeID` int(11), 
`fighterID` int(11),
FOREIGN KEY (`prizeID`) REFERENCES `Prizes`(`prizeID`),
FOREIGN KEY (`fighterID`) REFERENCES `Fighters`(`fighterID`)
);