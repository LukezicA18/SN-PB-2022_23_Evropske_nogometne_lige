--
-- File generated with SQLiteStudio v3.3.3 on tor. feb. 14 00:12:09 2023
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: League
CREATE TABLE `League` (
	`id`	INTEGER PRIMARY KEY AUTOINCREMENT,
	`country_id`	INTEGER,
	`name`	TEXT UNIQUE,
	FOREIGN KEY(`country_id`) REFERENCES `country`(`id`)
);
INSERT INTO League (id, country_id, name) VALUES (1729, 1729, 'England Premier League');
INSERT INTO League (id, country_id, name) VALUES (4769, 4769, 'France Ligue 1');
INSERT INTO League (id, country_id, name) VALUES (7809, 7809, 'Germany 1. Bundesliga');
INSERT INTO League (id, country_id, name) VALUES (10257, 10257, 'Italy Serie A');
INSERT INTO League (id, country_id, name) VALUES (21518, 21518, 'Spain LIGA BBVA');

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
