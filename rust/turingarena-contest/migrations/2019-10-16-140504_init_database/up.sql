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
    problem_name    TEXT NOT NULL REFERENCES problem(name),
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

CREATE TABLE evaluation_events(
    submission_id   TEXT NOT NULL REFERENCES submission(id),
    serial          INT  NOT NULL,
    event_json      TEXT NOT NULL,
    PRIMARY KEY(submission_id, serial)
)