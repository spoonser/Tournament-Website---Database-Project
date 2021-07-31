START TRANSACTION;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS Fighters;
DROP TABLE IF EXISTS Fights;
DROP TABLE IF EXISTS Prizes;
DROP TABLE IF EXISTS Weapons;
DROP TABLE IF EXISTS PrizesWon;
SET FOREIGN_KEY_CHECKS = 1;

--
-- Table structure for Weapons
--

CREATE TABLE `Weapons` (
`weaponID` int(11) NOT NULL AUTO_INCREMENT,
`weaponName` varchar(255) NOT NULL,
`weaponType` varchar(255) NOT NULL,
`ranged` boolean NOT NULL,
PRIMARY KEY (`weaponID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data for Weapons
INSERT INTO `Weapons` (`weaponID`, `weaponName`, `weaponType`, `ranged`) VALUES
(1, 'Mjolnir', 'Hammer', 0),
(2, 'Anduril', 'Sword', 0),
(3, 'Tristan', 'Bow', 1),
(4, 'Laser rifle', 'Gun', 1);

--
-- Table structure for Fighters
--

CREATE TABLE `Fighters` (
`fighterID` int(11) NOT NULL AUTO_INCREMENT,
`fighterName` varchar(255) NOT NULL,
`weapon` int(11),
PRIMARY KEY (`fighterID`),
FOREIGN KEY (`weapon`) REFERENCES Weapons(`weaponID`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data for Fighters
INSERT INTO `Fighters` (`fighterID`, `fighterName`, `weapon`) VALUES
(1, 'Thor', 1),
(2, 'Aragorn', 2),
(3, 'Annick', 3),
(4, 'Roberta Draper', NULL),
(5, 'Captain America', 1);

--
-- Table structure for Prizes
--

CREATE TABLE `Prizes` (
`prizeID` int(11) NOT NULL AUTO_INCREMENT,
`prizeType` varchar(255) NOT NULL,
PRIMARY KEY (`prizeID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data for Prizes
INSERT INTO `Prizes` (`prizeID`, `prizeType`) VALUES
(1, 'Best Move'),
(2, 'Best Costume'),
(3, 'Best Victory Dance'),
(4, 'Most Improved'),
(5, 'Most Creative');

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
`prize` int(11),
PRIMARY KEY (`fightID`),
FOREIGN KEY (`fighter1`) REFERENCES Fighters(`fighterID`),
FOREIGN KEY (`fighter2`) REFERENCES Fighters(`fighterID`), 
FOREIGN KEY (`prize`) REFERENCES Prizes(`prizeID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- Data for Fights
INSERT INTO `Fights` (`fightID`, `fightDate`, `fighter1`, `fighter2`, `fighter1Won`, `fighter2Won`, `prize`) VALUES
(1, '2021-07-01', 1, 2, 1, 0, 1),
(2, '2021-07-05', 2, 3, 0, 1, 2),
(3, '2021-07-10', 3, 4, 0, 1, 1),
(4, '2021-10-01', 1, 4, 0, 0, 2),
(5, '2021-07-02', 2, 4, 0, 1, 2),
(6, '2021-07-09', 4, 3, 1, 0, 1),
(7, '2021-07-15', 5, 2, 0, 0, NULL);
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

-- Data for PrizesWon
INSERT INTO `PrizesWon` (`fighterID`, `prizeID`) VALUES
(1, 1),
(3, 2),
(4, 1),
(4, 2);
