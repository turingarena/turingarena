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

CREATE TYPE submission_status_e AS ENUM ('RECEIVED', 'EVALUATING', 'EVALUATED');

CREATE TABLE submission (
  id         SERIAL PRIMARY KEY,
  problem    VARCHAR(50)         NOT NULL,
  contest_id INTEGER             NOT NULL REFERENCES contest (id) ON DELETE CASCADE,
  user_id    INTEGER             NOT NULL REFERENCES _user (id) ON DELETE CASCADE,
  timestamp  TIMESTAMP           NOT NULL DEFAULT CURRENT_TIMESTAMP,
  filename   VARCHAR(100)        NOT NULL CHECK (LENGTH(filename) > 0),
  status     submission_status_e NOT NULL DEFAULT 'RECEIVED'
);

CREATE TYPE event_type_e AS ENUM ('TEXT', 'DATA', 'FILE');

CREATE TABLE evaluation_event (
  submission_id INTEGER REFERENCES submission (id) ON DELETE CASCADE,
  serial        BIGSERIAL,
  type          event_type_e NOT NULL,
  data          TEXT,
  PRIMARY KEY (submission_id, serial)
);

CREATE TABLE user_contest (
  contest_id INTEGER REFERENCES contest (id) ON DELETE CASCADE,
  user_id    INTEGER REFERENCES _user (id) ON DELETE CASCADE,
  PRIMARY KEY (contest_id, user_id)
);

CREATE TABLE session (
  cookie     CHAR(64) PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES _user (id),
  timestamp  TIMESTAMP NOT NULL DEFAULT current_timestamp
);
