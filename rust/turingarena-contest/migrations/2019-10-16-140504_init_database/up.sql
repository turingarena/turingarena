CREATE TABLE problems(
    name            TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE users(
    id              TEXT NOT NULL PRIMARY KEY,
    display_name    TEXT NOT NULL,
    password        TEXT NOT NULL -- bcrypt encrypted
);

CREATE TABLE submissions(
    id              TEXT NOT NULL PRIMARY KEY,
    user_id         TEXT NOT NULL,
    problem_name    TEXT NOT NULL,
    created_at      TEXT NOT NULL
);

CREATE TABLE submission_files(
    submission_id   TEXT NOT NULL,
    field_id        TEXT NOT NULL,
    type_id         TEXT NOT NULL,
    name            TEXT NOT NULL,
    content_base64  TEXT NOT NULL,
    PRIMARY KEY (submission_id, field_id)
);
