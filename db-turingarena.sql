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

CREATE TABLE problem (
  id       SERIAL PRIMARY KEY,
  name     VARCHAR(100) UNIQUE NOT NULL CHECK (name SIMILAR TO '[a-zA-Z0-9_]+'),
  title    VARCHAR(100)        NOT NULL CHECK (LENGTH(title) > 0),
  location VARCHAR(100)        NOT NULL CHECK (LENGTH(location) > 0)
);

CREATE TABLE submission (
  id         SERIAL PRIMARY KEY,
  problem_id INTEGER      NOT NULL REFERENCES problem (id) ON DELETE CASCADE,
  user_id    INTEGER      NOT NULL REFERENCES _user (id) ON DELETE CASCADE,
  timestamp  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  filename   VARCHAR(100) NOT NULL CHECK (LENGTH(filename) > 0)
);

CREATE TABLE goal (
  id         SERIAL PRIMARY KEY,
  problem_id INTEGER REFERENCES problem (id) ON DELETE CASCADE,
  name       VARCHAR(100) NOT NULL CHECK (LENGTH(name) > 0),
  UNIQUE (problem_id, name)
);

CREATE TABLE acquired_goal (
  goal_id       INTEGER REFERENCES goal (id) ON DELETE CASCADE,
  submission_id INTEGER REFERENCES submission (id) ON DELETE CASCADE,
  PRIMARY KEY (goal_id, submission_id)
);

CREATE TYPE event_type_e AS ENUM ('TEXT', 'DATA', 'END');

CREATE TABLE evaluation_event (
  submission_id INTEGER REFERENCES submission (id) ON DELETE CASCADE,
  serial        SERIAL,
  type          event_type_e NOT NULL,
  data          TEXT,
  PRIMARY KEY (submission_id, serial)
);

CREATE TABLE contest (
  id     SERIAL PRIMARY KEY,
  name   VARCHAR(100) NOT NULL UNIQUE,
  public BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE user_contest (
  contest_id INTEGER REFERENCES contest (id) ON DELETE CASCADE,
  user_id    INTEGER REFERENCES _user (id) ON DELETE CASCADE,
  PRIMARY KEY (contest_id, user_id)
);

CREATE TABLE problem_contest (
  problem_id INTEGER REFERENCES problem (id) ON DELETE CASCADE,
  contest_id INTEGER REFERENCES contest (id) ON DELETE CASCADE,
  PRIMARY KEY (contest_id, problem_id)
);
