use diesel::prelude::*;
use diesel::sql_types::{Double, Text};
use juniper::FieldResult;

use schema::awards;
use schema_views::user_awards_view;

use crate::api::contest_submission::Submission;
use crate::api::root::ApiContext;

use super::super::award::*;
use super::*;
use crate::api::contest_evaluation::Evaluation;

#[derive(Insertable)]
#[table_name = "awards"]
pub struct AwardInput<'a> {
    pub evaluation_id: &'a str,
    pub award_name: &'a str,
    pub kind: &'a str,
    pub value: f64,
}

#[derive(Queryable, QueryableByName)]
pub struct AwardOutcomeData {
    /// Id of the evaluation
    #[allow(dead_code)]
    #[sql_type = "Text"]
    evaluation_id: String,

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
    pub fn list_by_user_and_problem<'a>(
        context: &'a ApiContext,
    ) -> FieldResult<Vec<AwardOutcome<'a>>> {
        Ok(user_awards_view::table
            .select((
                user_awards_view::evaluation_id,
                user_awards_view::award_name,
                user_awards_view::kind,
                user_awards_view::value,
            ))
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
        Ok(user_awards_view::table
            .filter(user_awards_view::user_id.eq(user_id))
            .filter(user_awards_view::problem_name.eq(problem_name))
            .select((
                user_awards_view::evaluation_id,
                user_awards_view::award_name,
                user_awards_view::kind,
                user_awards_view::value,
            ))
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
        Ok(awards::table
            .filter(awards::evaluation_id.eq(evaluation_id))
            .load(&context.database)?
            .into_iter()
            .map(|data| AwardOutcome { context, data })
            .collect())
    }

    pub fn evaluation_id(&self) -> &String {
        &self.data.evaluation_id
    }
}

#[juniper_ext::graphql]
impl AwardOutcome<'_> {
    fn evaluation(&self) -> FieldResult<Evaluation> {
        Evaluation::by_id(&self.context, &self.data.evaluation_id)
    }

    fn submission(&self) -> FieldResult<Submission> {
        Ok(self.evaluation()?.submission()?)
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
