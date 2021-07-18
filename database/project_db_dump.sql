SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Fighters;
DROP TABLE IF EXISTS Fights;
DROP TABLE IF EXISTS Prizes;
DROP TABLE IF EXISTS Weapons;
DROP TABLE IF EXISTS PrizesWon;
SET FOREIGN_KEY_CHECKS = 1;

--
-- Table structure for weapons
--

CREATE TABLE `Weapons` (
`weaponID` int(11) NOT NULL AUTO_INCREMENT,
`weaponName` varchar(255) NOT NULL,
`weaponType` varchar(255) NOT NULL,
`ranged` boolean NOT NULL,
PRIMARY KEY (`weaponID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for fighters
--

CREATE TABLE `Fighters` (
`fighterID` int(11) NOT NULL AUTO_INCREMENT,
`fighterName` varchar(255) NOT NULL,
`weapon` int(11),
PRIMARY KEY (`fighterID`),
FOREIGN KEY (`weapon`) REFERENCES Weapons(`weaponID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


--
-- Table structure for fights
--

CREATE TABLE `Fights` (
`fightID` int(11) NOT NULL AUTO_INCREMENT,
`fightDate` date NOT NULL,
`fighter1` int(11) DEFAULT NULL,
`fighter2` int(11) DEFAULT NULL,
`fighter1Won` boolean DEFAULT 0,
`fighter2Won` boolean DEFAULT 0,
PRIMARY KEY (`fightID`),
FOREIGN KEY (`fighter1`) REFERENCES Fighters(`fighterID`),
FOREIGN KEY (`fighter2`) REFERENCES Fighters(`fighterID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for prizes
--

CREATE TABLE `Prizes` (
`prizeID` int(11) NOT NULL AUTO_INCREMENT,
`prizeType` varchar(255) NOT NULL,
PRIMARY KEY (`prizeID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for prizesWon
--

CREATE TABLE `PrizesWon` (
`fighterID` int(11) NOT NULL,
`prizeID` int(11) NOT NULL,
PRIMARY KEY (`fighterID`, `prizeID`),
FOREIGN KEY (`fighterID`) REFERENCES Fighters(`fighterID`),
FOREIGN KEY (`prizeID`) REFERENCES Prizes(`prizeID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
