DELETE
FROM submission;
DELETE
FROM problem;
DELETE
FROM _user;
INSERT INTO _user (first_name, last_name, username, email, password, privilege)
VALUES ('Alessandro',
        'Righi',
        'alerighi',
        'alessandro.righi@outlook.it',
        '$2b$12$9lqPbs8eY9vELJyN7Xo/TuzPzwZcoWw1MasxbVkIk5i.ZD536UbbK',
        'ADMIN');
