CREATE TABLE problems
(
    name              TEXT NOT NULL PRIMARY KEY,
    archive_integrity TEXT NOT NULL
);

CREATE TABLE users
(
    id           TEXT NOT NULL PRIMARY KEY,
    display_name TEXT NOT NULL,
    token        TEXT NOT NULL UNIQUE
);

CREATE TABLE submissions
(
    id           TEXT NOT NULL PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users (id),
    problem_name TEXT NOT NULL REFERENCES problems (name),
    created_at   TEXT NOT NULL
);

CREATE TABLE submission_files
(
    submission_id TEXT NOT NULL REFERENCES submissions (id),
    field_id      TEXT NOT NULL,
    type_id       TEXT NOT NULL,
    name          TEXT NOT NULL,
    content       BLOB NOT NULL,
    PRIMARY KEY (submission_id, field_id)
);

CREATE TABLE evaluations
(
    id            TEXT NOT NULL PRIMARY KEY,
    submission_id TEXT NOT NULL REFERENCES submissions (id),
    created_at    TEXT NOT NULL,
    status        TEXT NOT NULL CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED'))
);

CREATE TABLE evaluation_events
(
    evaluation_id TEXT NOT NULL REFERENCES evaluations (id),
    serial        INT  NOT NULL,
    event_json    TEXT NOT NULL,
    PRIMARY KEY (evaluation_id, serial)
);

CREATE TABLE awards
(
    evaluation_id TEXT   NOT NULL REFERENCES evaluations (id),
    award_name    TEXT   NOT NULL,
    kind          TEXT   NOT NULL CHECK (kind IN ('SCORE', 'BADGE')),
    value         DOUBLE NOT NULL,
    PRIMARY KEY (evaluation_id, award_name, kind)
);

CREATE TABLE contest
(
    id                INT  NOT NULL PRIMARY KEY DEFAULT 0 CHECK (id = 0), -- to ensure this table has a single row
    archive_integrity TEXT NOT NULL,
    start_time        TEXT NOT NULL,
    end_time          TEXT NOT NULL
);

CREATE TABLE questions
(
    id           INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id      TEXT    NOT NULL REFERENCES users (id),
    problem_name TEXT REFERENCES problems (name),
    time         TEXT    NOT NULL,
    text         TEXT    NOT NULL
);

CREATE TABLE answers
(
    question_id INT  NOT NULL PRIMARY KEY REFERENCES questions (id),
    text        TEXT NOT NULL
);

CREATE TABLE announcements
(
    id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    text TEXT    NOT NULL
);

CREATE TABLE blobs
(
    integrity TEXT NOT NULL PRIMARY KEY,
    content   BLOB NOT NULL
);

CREATE VIEW user_awards_view AS
    WITH successful_evaluations AS (
        SELECT e.*
        FROM evaluations e
        WHERE e.status = 'SUCCESS'
    ),
         official_evaluations AS (
             SELECT e.*
             FROM successful_evaluations e
             WHERE e.id = (
                 SELECT e2.id
                 FROM successful_evaluations e2
                 WHERE e2.submission_id = e.submission_id
                 ORDER BY e2.created_at DESC
                 LIMIT 1
             )),
         submission_awards AS (
             SELECT a.*, s.id as submission_id, s.user_id, s.problem_name, s.created_at
             FROM awards a
                      JOIN official_evaluations e ON a.evaluation_id = e.id
                      JOIN submissions s ON e.submission_id = s.id
         )
    SELECT a.user_id,
           a.problem_name,
           a.award_name,
           a.kind,
           a.value,
           a.evaluation_id
    FROM submission_awards a
    WHERE a.submission_id = (
        SELECT a2.submission_id
        FROM submission_awards a2
        WHERE a2.user_id = a.user_id
          AND a2.problem_name = a.problem_name
          AND a2.award_name = a.award_name
          AND a2.kind = a.kind
        ORDER BY a2.value DESC, a2.created_at
        LIMIT 1
    );
