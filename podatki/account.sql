
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;


CREATE TABLE Account (
	id	INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE,
    password TEXT,
    budget INTEGER,
    team_id INTEGER REFERENCES Team (team_api_id)
);
INSERT INTO Account (id, username, password, budget, team_id) VALUES (1, 'racun', 'nimamgesla', 500000000, 500000);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
