--
-- File generated with SQLiteStudio v3.3.3 on tor. feb. 14 00:11:28 2023
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: Country
CREATE TABLE `Country` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`name`	TEXT UNIQUE
);
INSERT INTO Country (id, name) VALUES (1729, 'England');
INSERT INTO Country (id, name) VALUES (4769, 'France');
INSERT INTO Country (id, name) VALUES (7809, 'Germany');
INSERT INTO Country (id, name) VALUES (10257, 'Italy');
INSERT INTO Country (id, name) VALUES (21518, 'Spain');

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
