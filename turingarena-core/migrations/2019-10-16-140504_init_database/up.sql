CREATE TABLE problems(
    name            TEXT NOT NULL PRIMARY KEY,
    archive_content BLOB NOT NULL
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
    created_at      TEXT NOT NULL
);

CREATE TABLE submission_files(
    submission_id   TEXT NOT NULL REFERENCES submissions(id),
    field_id        TEXT NOT NULL,
    type_id         TEXT NOT NULL,
    name            TEXT NOT NULL,
    content         BLOB NOT NULL,
    PRIMARY KEY (submission_id, field_id)
);

CREATE TABLE evaluations(
    id              TEXT NOT NULL PRIMARY KEY,
    submission_id   TEXT NOT NULL REFERENCES submissions(id),
    created_at      TEXT NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED'))
);

CREATE TABLE evaluation_events(
    evaluation_id   TEXT NOT NULL REFERENCES evaluations(id),
    serial          INT  NOT NULL,
    event_json      TEXT NOT NULL,
    PRIMARY KEY (evaluation_id, serial)
);

CREATE TABLE evaluation_awards(
    evaluation_id   TEXT   NOT NULL REFERENCES evaluations(id),
    award_name      TEXT   NOT NULL,
    kind            TEXT   NOT NULL CHECK (kind IN ('SCORE', 'BADGE')),
    value           DOUBLE NOT NULL,
    PRIMARY KEY (evaluation_id, award_name)
);

CREATE TABLE contest(
    id              INT  NOT NULL PRIMARY KEY DEFAULT 0 CHECK (id = 0), -- to ensure this table has a single row
    archive_content BLOB NOT NULL,
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