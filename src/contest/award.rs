use super::super::award::*;
use super::*;

use diesel::prelude::*;
use diesel::sql_types::{Bool, Double, Text};

use schema::awards;

#[derive(Insertable)]
#[table_name = "awards"]
pub struct AwardInput<'a> {
    pub kind: &'a str,
    pub submission_id: &'a str,
    pub award_name: &'a str,
    pub value: f64,
}

#[derive(Queryable, QueryableByName)]
pub struct AwardData {
    #[allow(dead_code)]
    #[sql_type = "Text"]
    kind: String,

    /// Id of the submission
    #[allow(dead_code)]
    #[sql_type = "Text"]
    submission_id: String,

    /// Name of the award
    #[sql_type = "Text"]
    award_name: String,

    #[sql_type = "Double"]
    value: f64,
}

pub struct ScoreAward {
    pub data: AwardData,
}

pub struct BadgeAward {
    pub data: AwardData,
}

#[juniper::object]
impl ScoreAward {
    /// Id of the most recent submission that made the max score
    fn submission_id(&self) -> &String {
        &self.data.submission_id
    }

    /// The score
    fn score(&self) -> Score {
        Score(self.data.value)
    }

    /// Name of the award
    fn award_name(&self) -> AwardName {
        AwardName(self.data.award_name.clone())
    }
}

#[juniper::object]
impl BadgeAward {
    /// Id of the most recent submission that made the max score
    fn submission_id(&self) -> &String {
        &self.data.submission_id
    }

    /// The badge
    fn badge(&self) -> bool {
        self.data.value == 1f64
    }

    /// Name of the award
    fn award_name(&self) -> AwardName {
        AwardName(self.data.award_name.clone())
    }
}

/// Get the best score award for (user, problem)
pub fn query_awards_of_user_and_problem(
    conn: &SqliteConnection,
    kind: &str,
    user_id: &str,
    problem_name: &str,
) -> QueryResult<Vec<AwardData>> {
    diesel::sql_query(
        "
        SELECT sc.kind, sc.award_name, MAX(sc.value) as value, (
            SELECT s.id
            FROM submissions s JOIN awards sci ON s.id = sci.submission_id
            WHERE sci.value = value AND sci.kind = sc.kind AND sci.award_name = sc.award_name
            ORDER BY s.created_at DESC
            LIMIT 1
        ) as submission_id
        FROM awards sc JOIN submissions s ON sc.submission_id = s.id
        WHERE sc.kind = ? AND s.problem_name = ? AND s.user_id = ?
        GROUP BY sc.award_name
    ",
    )
    .bind::<Text, _>(kind)
    .bind::<Text, _>(problem_name)
    .bind::<Text, _>(user_id)
    .load::<AwardData>(conn)
}

/// Get the awards of (user, problem, submission)
pub fn query_awards(
    conn: &SqliteConnection,
    kind: &str,
    submission_id: &str,
) -> QueryResult<Vec<AwardData>> {
    awards::table
        .filter(awards::dsl::kind.eq(kind))
        .filter(awards::dsl::submission_id.eq(submission_id))
        .load(conn)
}
