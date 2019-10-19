table! {
    problems (name) {
        name -> Text,
    }
}

table! {
    submission_files (submission_id, field_id) {
        submission_id -> Text,
        field_id -> Text,
        type_id -> Text,
        name -> Text,
        content -> Binary,
    }
}

table! {
    submissions (id) {
        id -> Text,
        user_id -> Text,
        problem_name -> Text,
        created_at -> Text,
    }
}

table! {
    users (id) {
        id -> Text,
        display_name -> Text,
        password_bcrypt -> Text,
    }
}

joinable!(submission_files -> submissions (submission_id));
joinable!(submissions -> users (user_id));

allow_tables_to_appear_in_same_query!(
    problems,
    submission_files,
    submissions,
    users,
);
