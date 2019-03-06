-- Postgres database for TuringArena web interface

DROP SCHEMA PUBLIC CASCADE;
CREATE SCHEMA PUBLIC;

CREATE TYPE user_privilege_e AS ENUM ('STANDARD', 'ADMIN', 'TUTOR');

CREATE TABLE _user (
  id         SERIAL PRIMARY KEY,
  first_name VARCHAR(30)      NOT NULL CHECK (LENGTH(first_name) > 0),
  last_name  VARCHAR(30)      NOT NULL CHECK (LENGTH(last_name) > 0),
  username   VARCHAR(30)      NOT NULL UNIQUE CHECK (LENGTH(username) > 0),
  email      VARCHAR(100)     NOT NULL CHECK (email SIMILAR TO '[^@]+@[^@]+\.[^@]+'),
  password   CHAR(60)         NOT NULL, -- bcrypt.hashpw password stored in hex format
  privilege  user_privilege_e NOT NULL DEFAULT 'STANDARD'
);

CREATE TABLE submission (
  id         SERIAL PRIMARY KEY,
  problem    VARCHAR(50)         NOT NULL,
  contest    VARCHAR(50)         NOT NULL,
  user_id    INTEGER             NOT NULL REFERENCES _user (id) ON DELETE CASCADE,
  timestamp  TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP,
  filename   VARCHAR(100)        NOT NULL CHECK (LENGTH(filename) > 0)
);

CREATE TYPE event_type_e AS ENUM ('TEXT', 'DATA', 'FILE');

CREATE TABLE user_contest (
  contest    VARCHAR(50)         NOT NULL,
  user_id    INTEGER             NOT NULL REFERENCES _user (id) ON DELETE CASCADE,
  PRIMARY KEY (contest, user_id)
);
