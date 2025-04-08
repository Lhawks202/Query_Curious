-- this is the schema for the dances
CREATE TABLE Dance (
	DanceId INTEGER PRIMARY KEY,
	Vlink TEXT,
	Date TEXT,
	Source TEXT,
	StepsId INTEGER NOT NULL,
	FOREIGN KEY (StepsId) REFERENCES Steps (StepsId)
);

CREATE TABLE Steps (
	StepsId INTEGER PRIMARY KEY,
	Sequence TEXT,
	FigureId INTEGER NOT NULL,
	FOREIGN KEY (FigureId) REFERENCES Figure (FigureId)
);

CREATE TABLE User (
	UserId INTEGER PRIMARY KEY,
	Name TEXT NOT NULL,
	Email TEXT NOT NULL,
	State TEXT,
	City TEXT
);

CREATE TABLE Figure (
	FigureId INTEGER PRIMARY KEY,
	Move: TEXT NOT NULL
);

CREATE TABLE Learning (
	LearningId INTEGER PRIMARY KEY AUTOINCREMENT,
	UserId TEXT,
	DanceId TEXT,
	DateAdded TEXT,
	FOREIGN KEY (UserId) REFERENCES User (UserId),
	FOREIGN KEY (DanceId) REFERENCES Dance (DanceId)
);

CREATE TABLE Favorites (
	FavoritesId INTEGER PRIMARY KEY AUTOINCREMENT,
	UserId TEXT,
	DanceId TEXT,
	DateAdded TEXT,
	Rating INTEGER,
	FOREIGN KEY (UserId) REFERENCES User (UserId),
	FOREIGN KEY (DanceId) REFERENCES Dance (DanceId)
);

CREATE TABLE FigureStep (
	StepsId INTEGER,
	FigureId INTEGER,
	Place TEXT,
	PRIMARY KEY (StepId, FigureId),
	FOREIGN KEY (FigureId) REFERENCES Figure (FigureId),
	FOREIGN KEY (StepsId) REFERENCES Steps (StepsId)
);
