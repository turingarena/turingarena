CREATE TABLE problems(
    name            TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE users(
    id              TEXT NOT NULL PRIMARY KEY,
    display_name    TEXT NOT NULL,
    token           TEXT NOT NULL UNIQUE
);

CREATE TABLE submissions(
    id              TEXT NOT NULL PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(id),
    problem_name    TEXT NOT NULL REFERENCES problems(name),
    created_at      TEXT NOT NULL, 
    status          TEXT NOT NULL CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED'))
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

CREATE TABLE badge_awards(
    submission_id   TEXT   NOT NULL REFERENCES submissions(id),
    award_name      TEXT   NOT NULL,
    badge           BOOLEAN NOT NULL,
    PRIMARY KEY (submission_id, award_name)
);

CREATE TABLE score_awards(
    submission_id   TEXT   NOT NULL REFERENCES submissions(id),
    award_name      TEXT   NOT NULL,
    score           DOUBLE NOT NULL,
    PRIMARY KEY (submission_id, award_name)
);

CREATE TABLE contest(
    id              INT  NOT NULL PRIMARY KEY DEFAULT 0 CHECK (id = 0), -- to ensure this table has a single row
    start_time      TEXT NOT NULL,
    end_time        TEXT NOT NULL
);

CREATE TABLE questions(
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id         TEXT NOT NULL REFERENCES users(id),
    problem_name    TEXT REFERENCES problems(name),
    time            TEXT NOT NULL,
    text            TEXT NOT NULL
);

CREATE TABLE answers(
    question_id     INT NOT NULL PRIMARY KEY REFERENCES questions(id),
    text            TEXT NOT NULL
);

CREATE TABLE announcements(
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    text            TEXT NOT NULL
);