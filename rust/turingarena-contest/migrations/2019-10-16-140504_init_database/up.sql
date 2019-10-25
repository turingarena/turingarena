CREATE TABLE problems(
    name            TEXT NOT NULL PRIMARY KEY,
    path            TEXT NOT NULL
);

CREATE TABLE users(
    id              TEXT NOT NULL PRIMARY KEY,
    display_name    TEXT NOT NULL,
    password_bcrypt TEXT NOT NULL
);

CREATE TABLE submissions(
    id              TEXT NOT NULL PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(id),
    problem_name    TEXT NOT NULL REFERENCES problems(name),
    created_at      TEXT NOT NULL, 
    status          TEXT NOT NULL CHECK(status IN ('PENDING', 'SUCCESS', 'FAILED'))
);

CREATE TABLE submission_files(
    submission_id   TEXT NOT NULL REFERENCES submissions(id),
    field_id        TEXT NOT NULL,
    type_id         TEXT NOT NULL,
    name            TEXT NOT NULL,
    content         BLOB NOT NULL,
    PRIMARY KEY (submission_id, field_id)
);

CREATE TABLE evaluation_events(
    submission_id   TEXT NOT NULL REFERENCES submissions(id),
    serial          INT  NOT NULL,
    event_json      TEXT NOT NULL,
    PRIMARY KEY (submission_id, serial)
);

CREATE TABLE scorables(
    submission_id   TEXT   NOT NULL REFERENCES submissions(id),
    scorable_id     TEXT   NOT NULL,
    score           DOUBLE NOT NULL,
    PRIMARY KEY (submission_id, scorable_id)
);

CREATE TABLE config(
    id              INT  NOT NULL PRIMARY KEY DEFAULT 0 CHECK (id = 0), -- to ensure this table has a single row
    contest_title   TEXT NOT NULL, 
    start_time      TEXT NOT NULL,
    end_time        TEXT NOT NULL
);
