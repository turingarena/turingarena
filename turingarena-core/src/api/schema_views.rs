table! {
    user_awards_view (user_id, problem_name, award_name, kind) {
        user_id -> Text,
        problem_name -> Text,
        award_name -> Text,
        kind -> Text,
        value -> Double,
        evaluation_id -> Text,
    }
}
