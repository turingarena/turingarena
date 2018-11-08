-- Postgres database for TuringArena web interface

DROP SCHEMA PUBLIC CASCADE;
CREATE SCHEMA PUBLIC;

CREATE TYPE user_privilege_e AS ENUM ('STANDARD', 'ADMIN', 'TUTOR');

CREATE TABLE _user(
    id              SERIAL          PRIMARY KEY,
    first_name      VARCHAR(30)     NOT NULL CHECK (LENGTH(first_name) > 0),
    last_name       VARCHAR(30)     NOT NULL CHECK (LENGTH(last_name) > 0),
    username        VARCHAR(30)     NOT NULL UNIQUE CHECK (LENGTH(username) > 0),
    email           VARCHAR(100)    NOT NULL CHECK (email SIMILAR TO '[^@]+@[^@]+\.[^@]+'),
    password        CHAR(60)        NOT NULL, -- bcrypt.hashpw password stored in hex format
    privilege       user_privilege_e NOT NULL DEFAULT 'STANDARD'
);

CREATE TABLE problem(
  id       SERIAL          PRIMARY KEY,
  name     VARCHAR(100)    UNIQUE NOT NULL CHECK (LENGTH(name) > 0),
  title    VARCHAR(100)           NOT NULL CHECK (LENGTH(title) > 0),
  location VARCHAR(100)           NOT NULL CHECK (LENGTH(location) > 0),
  path     VARCHAR(200)           NOT NULL CHECK (LENGTH(path) > 0)
);

CREATE TABLE submission(
  id         SERIAL          PRIMARY KEY,
  problem_id INTEGER      NOT NULL REFERENCES problem(id),
  user_id    INTEGER      NOT NULL REFERENCES _user(id),
  timestamp  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  filename   VARCHAR(100) NOT NULL CHECK (LENGTH(filename) > 0),
  path       VARCHAR(100) NOT NULL
);

CREATE TABLE goal(
    id              SERIAL          PRIMARY KEY,
    problem_id      INTEGER         REFERENCES problem(id),
    name            VARCHAR(100)    NOT NULL CHECK (LENGTH(name) > 0),
    UNIQUE(problem_id, name)
);

CREATE TABLE acquired_goal(
    goal_id         INTEGER         REFERENCES goal(id),
    submission_id   INTEGER         REFERENCES submission(id),
    PRIMARY KEY(goal_id, submission_id)
);

CREATE TYPE event_type_e AS ENUM ('TEXT', 'DATA');

CREATE TABLE evaluation_event(
    submission_id   INTEGER         REFERENCES submission(id),
    serial          SERIAL,
    type            event_type_e    NOT NULL,
    data            TEXT            NOT NULL,
    PRIMARY KEY(submission_id, serial)
);
