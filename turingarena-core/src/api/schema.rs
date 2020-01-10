table! {
    awards (evaluation_id, award_name, kind) {
        evaluation_id -> Text,
        award_name -> Text,
        kind -> Text,
        value -> Double,
    }
}

table! {
    blobs (integrity) {
        integrity -> Text,
        content -> Binary,
    }
}

table! {
    contest (id) {
        id -> Integer,
        archive_integrity -> Text,
        start_time -> Text,
        end_time -> Text,
    }
}

table! {
    evaluation_events (evaluation_id, serial) {
        evaluation_id -> Text,
        serial -> Integer,
        event_json -> Text,
    }
}

table! {
    evaluations (id) {
        id -> Text,
        submission_id -> Text,
        created_at -> Text,
        status -> Text,
    }
}

table! {
    message_engagements (message_id, user_id, engagement) {
        message_id -> Text,
        user_id -> Text,
        engagement -> Text,
        created_at -> Text,
    }
}

table! {
    messages (id) {
        id -> Text,
        created_at -> Text,
        kind -> Text,
        user_id -> Nullable<Text>,
        problem_name -> Nullable<Text>,
        text -> Text,
    }
}

table! {
    problems (name) {
        name -> Text,
        archive_integrity -> Text,
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
        token -> Text,
        admin -> Bool,
    }
}

joinable!(awards -> evaluations (evaluation_id));
joinable!(evaluation_events -> evaluations (evaluation_id));
joinable!(evaluations -> submissions (submission_id));
joinable!(message_engagements -> messages (message_id));
joinable!(messages -> problems (problem_name));
joinable!(messages -> users (user_id));
joinable!(submission_files -> submissions (submission_id));
joinable!(submissions -> problems (problem_name));
joinable!(submissions -> users (user_id));

allow_tables_to_appear_in_same_query!(
    awards,
    blobs,
    contest,
    evaluation_events,
    evaluations,
    message_engagements,
    messages,
    problems,
    submission_files,
    submissions,
    users,
);
