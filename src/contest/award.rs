use super::super::award::*;
use super::*;

use diesel::prelude::*;
use diesel::sql_types::{Bool, Double, Text};

use crate::contest::api::ApiContext;
use juniper::FieldResult;
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

pub struct SubmissionAward {
    data: AwardData,
}

impl SubmissionAward {
    /// Get the best score award for (user, problem)
    pub fn by_user_and_problem(
        context: &ApiContext,
        user_id: &str,
        problem_name: &str,
    ) -> FieldResult<Vec<SubmissionAward>> {
        Ok(diesel::sql_query("
                SELECT sc.kind, sc.award_name, MAX(sc.value) as value, (
                    SELECT s.id
                    FROM submissions s JOIN awards sci ON s.id = sci.submission_id
                    WHERE sci.value = value AND sci.kind = sc.kind AND sci.award_name = sc.award_name
                    ORDER BY s.created_at DESC
                    LIMIT 1
                ) as submission_id
                FROM awards sc JOIN submissions s ON sc.submission_id = s.id
                WHERE s.problem_name = ? AND s.user_id = ?
                GROUP BY sc.award_name
            ")
            .bind::<Text, _>(problem_name)
            .bind::<Text, _>(user_id)
            .load::<AwardData>(&context.database)?
            .into_iter()
            .map(|data| SubmissionAward { data })
            .collect())
    }

    /// Get the awards of (user, problem, submission)
    pub fn of_submission(
        context: &ApiContext,
        submission_id: &str,
    ) -> FieldResult<Vec<SubmissionAward>> {
        Ok(awards::table
            .filter(awards::dsl::submission_id.eq(submission_id))
            .load(&context.database)?
            .into_iter()
            .map(|data| SubmissionAward { data })
            .collect())
    }
}

#[juniper_ext::graphql]
impl SubmissionAward {
    /// Id of the most recent submission that made the max score
    fn submission_id(&self) -> &String {
        &self.data.submission_id
    }

    /// Name of the award
    fn award_name(&self) -> AwardName {
        AwardName(self.data.award_name.clone())
    }

    fn value(&self) -> AwardValue {
        match self.data.kind.as_ref() {
            "SCORE" => AwardValue::Score(ScoreAwardValue {
                score: Score(self.data.value),
            }),
            "BADGE" => AwardValue::Badge(BadgeAwardValue {
                badge: self.data.value == 1f64,
            }),
            _ => unreachable!(),
        }
    }
}

#[derive(juniper_ext::GraphQLUnionFromEnum)]
pub enum AwardValue {
    Score(ScoreAwardValue),
    Badge(BadgeAwardValue),
}

#[derive(juniper::GraphQLObject)]
pub struct ScoreAwardValue {
    pub score: Score,
}

#[derive(juniper::GraphQLObject)]
pub struct BadgeAwardValue {
    pub badge: bool,
}
