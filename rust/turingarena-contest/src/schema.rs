table! {
    evaluation_events (submission_id, serial) {
        submission_id -> Text,
        serial -> Integer,
        event_json -> Text,
    }
}

table! {
    problems (name) {
        name -> Text,
        path -> Text,
    }
}

table! {
    scorables (submission_id, scorable_id) {
        submission_id -> Text,
        scorable_id -> Text,
        score -> Double,
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
    evaluation_events,
    problems,
    scorables,
    submission_files,
    submissions,
    users,
);
