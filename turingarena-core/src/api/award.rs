use diesel::prelude::*;
use diesel::sql_types::{Double, Text};
use juniper::FieldResult;

use schema::awards;
use schema_views::user_awards_view;

use crate::api::contest_evaluation::Evaluation;
use crate::api::contest_submission::Submission;
use crate::api::root::ApiContext;

use super::super::award::*;
use super::*;

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
    evaluation_id: Option<String>,

    #[allow(dead_code)]
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
    award: Award,
    data: AwardOutcomeData,
}

impl AwardOutcome<'_> {
    /// Get the best score award for (user, problem)
    pub fn find_best<'a>(
        context: &'a ApiContext<'a>,
        award: &Award,
        user_id: &str,
        problem_name: &str,
    ) -> FieldResult<AwardOutcome<'a>> {
        let kind = match award.content {
            AwardContent::Score(_) => "SCORE",
            AwardContent::Badge(_) => "BADGE",
        };
        let data = user_awards_view::table
            .find((user_id, problem_name, &award.name.0, &kind))
            .select((
                user_awards_view::evaluation_id.nullable(),
                user_awards_view::award_name,
                user_awards_view::kind,
                user_awards_view::value,
            ))
            .first(&context.database)
            .optional()?
            .unwrap_or(AwardOutcomeData {
                evaluation_id: None,
                award_name: award.name.0.to_owned(),
                value: 0f64,
                kind: kind.to_owned(),
            });
        Ok(AwardOutcome {
            award: (*award).clone(),
            context,
            data,
        })
    }

    /// Find the outcome of an award in a given evaluation
    pub fn find<'a>(
        context: &'a ApiContext<'a>,
        award: &Award,
        evaluation_id: &str,
    ) -> FieldResult<AwardOutcome<'a>> {
        let kind = match award.content {
            AwardContent::Score(_) => "SCORE",
            AwardContent::Badge(_) => "BADGE",
        };
        let data = awards::table
            .find((evaluation_id, &award.name.0, &kind))
            .select((
                awards::evaluation_id.nullable(),
                awards::award_name,
                awards::kind,
                awards::value,
            ))
            .first(&context.database)
            .optional()?
            .unwrap_or(AwardOutcomeData {
                evaluation_id: Some(evaluation_id.to_owned()),
                award_name: award.name.0.to_owned(),
                value: 0f64,
                kind: kind.to_owned(),
            });
        Ok(AwardOutcome {
            award: (*award).clone(),
            context,
            data,
        })
    }

    pub fn total_score(awards: &Vec<Self>) -> Score {
        Score(
            awards
                .iter()
                .filter_map(|award| match award.value() {
                    AwardValue::Score(ScoreAwardValue {
                        score: Score(score),
                    }) => Some(score),
                    _ => None,
                })
                .sum(),
        )
    }
}

#[juniper_ext::graphql]
impl AwardOutcome<'_> {
    fn evaluation(&self) -> FieldResult<Option<Evaluation>> {
        Ok(match &self.data.evaluation_id {
            Some(id) => Some(Evaluation::by_id(&self.context, id)?),
            None => None,
        })
    }

    fn submission(&self) -> FieldResult<Option<Submission>> {
        Ok(match self.evaluation()? {
            Some(evaluation) => Some(evaluation.submission()?),
            None => None,
        })
    }

    pub fn award(&self) -> &Award {
        &self.award
    }

    pub fn value(&self) -> AwardValue {
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
