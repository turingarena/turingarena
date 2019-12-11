use super::super::award::*;
use super::*;

use diesel::prelude::*;
use diesel::sql_types::{Bool, Double, Text};

use crate::contest::api::ApiContext;
use crate::contest::contest_submission::Submission;
use juniper::FieldResult;
use schema::evaluation_awards;

#[derive(Insertable)]
#[table_name = "evaluation_awards"]
pub struct AwardInput<'a> {
    pub evaluation_id: &'a str,
    pub award_name: &'a str,
    pub kind: &'a str,
    pub value: f64,
}

#[derive(Queryable, QueryableByName)]
pub struct AwardOutcomeData {
    /// Id of the submission
    #[allow(dead_code)]
    #[sql_type = "Text"]
    submission_id: String,

    /// Name of the award
    #[sql_type = "Text"]
    award_name: String,

    #[allow(dead_code)]
    #[sql_type = "Text"]
    kind: String,

    #[sql_type = "Double"]
    value: f64,
}

pub struct AwardOutcome<'a> {
    context: &'a ApiContext<'a>,
    data: AwardOutcomeData,
}

impl AwardOutcome<'_> {
    const BY_USER_AND_PROBLEM_SQL: &'static str = "
        SELECT a.kind, a.award_name, MAX(a.value) as value, (
            SELECT s2.id
            FROM evaluation_awards a2 JOIN evaluations e2 ON a2.evaluation_id = e2.id JOIN submissions s2 ON e2.submission_id = s2.id
            WHERE a2.value = value AND a2.kind = a.kind AND a2.award_name = a.award_name
                AND s2.problem_name = s.problem_name AND s2.user_id = s.user_id
            ORDER BY s2.created_at DESC
            LIMIT 1
        ) as submission_id
        FROM evaluation_awards a JOIN evaluations e ON a.evaluation_id = e.id JOIN submissions s ON e.submission_id = s.id
        GROUP BY s.problem_name, a.kind, a.award_name, s.user_id
    ";

    pub fn list_by_user_and_problem<'a>(
        context: &'a ApiContext,
    ) -> FieldResult<Vec<AwardOutcome<'a>>> {
        Ok(diesel::sql_query(Self::BY_USER_AND_PROBLEM_SQL)
            .load::<AwardOutcomeData>(&context.database)?
            .into_iter()
            .map(|data| AwardOutcome { context, data })
            .collect())
    }

    /// Get the best score award for (user, problem)
    pub fn by_user_and_problem<'a>(
        context: &'a ApiContext,
        user_id: &str,
        problem_name: &str,
    ) -> FieldResult<Vec<AwardOutcome<'a>>> {
        Ok(diesel::sql_query(format!(
            "
                {}
                HAVING s.problem_name = ? AND s.user_id = ?
            ",
            Self::BY_USER_AND_PROBLEM_SQL
        ))
        .bind::<Text, _>(problem_name)
        .bind::<Text, _>(user_id)
        .load::<AwardOutcomeData>(&context.database)?
        .into_iter()
        .map(|data| AwardOutcome { context, data })
        .collect())
    }

    /// Get the awards of (user, problem, submission)
    pub fn of_evaluation<'a>(
        context: &'a ApiContext<'a>,
        evaluation_id: &str,
    ) -> FieldResult<Vec<AwardOutcome<'a>>> {
        Ok(diesel::sql_query(
            "
                SELECT a.kind, a.award_name, a.value, e.submission_id
                FROM evaluation_awards a JOIN evaluations e ON a.evaluation_id = e.id
                WHERE e.id = ?
            ",
        )
        .bind::<Text, _>(evaluation_id)
        .load(&context.database)?
        .into_iter()
        .map(|data| AwardOutcome { context, data })
        .collect())
    }

    pub fn submission_id(&self) -> &String {
        &self.data.submission_id
    }
}

#[juniper_ext::graphql]
impl AwardOutcome<'_> {
    fn submission(&self) -> FieldResult<Submission> {
        Submission::by_id(&self.context, &self.data.submission_id)
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
