table! {
    announcements (id) {
        id -> Integer,
        text -> Text,
    }
}

table! {
    answers (question_id) {
        question_id -> Integer,
        text -> Text,
    }
}

table! {
    awards (submission_id, award_name) {
        kind -> Text,
        submission_id -> Text,
        award_name -> Text,
        value -> Double,
    }
}

table! {
    contest (id) {
        id -> Integer,
        archive_content -> Binary,
        start_time -> Text,
        end_time -> Text,
    }
}

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
        archive_content -> Binary,
    }
}

table! {
    questions (id) {
        id -> Integer,
        user_id -> Text,
        problem_name -> Nullable<Text>,
        time -> Text,
        text -> Text,
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
        status -> Text,
    }
}

table! {
    users (id) {
        id -> Text,
        display_name -> Text,
        token -> Text,
    }
}

joinable!(answers -> questions (question_id));
joinable!(awards -> submissions (submission_id));
joinable!(evaluation_events -> submissions (submission_id));
joinable!(questions -> problems (problem_name));
joinable!(questions -> users (user_id));
joinable!(submission_files -> submissions (submission_id));
joinable!(submissions -> problems (problem_name));
joinable!(submissions -> users (user_id));

allow_tables_to_appear_in_same_query!(
    announcements,
    answers,
    awards,
    contest,
    evaluation_events,
    problems,
    questions,
    submission_files,
    submissions,
    users,
);
