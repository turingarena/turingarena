table! {
    badge_awards (submission_id, award_name) {
        submission_id -> Text,
        award_name -> Text,
        badge -> Bool,
    }
}

table! {
    contest (id) {
        id -> Integer,
        title -> Text,
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
    }
}

table! {
    score_awards (submission_id, award_name) {
        submission_id -> Text,
        award_name -> Text,
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

joinable!(badge_awards -> submissions (submission_id));
joinable!(evaluation_events -> submissions (submission_id));
joinable!(score_awards -> submissions (submission_id));
joinable!(submission_files -> submissions (submission_id));
joinable!(submissions -> problems (problem_name));
joinable!(submissions -> users (user_id));

allow_tables_to_appear_in_same_query!(
    badge_awards,
    contest,
    evaluation_events,
    problems,
    score_awards,
    submission_files,
    submissions,
    users,
);
