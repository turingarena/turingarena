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
use crate::api::contest_problem::Problem;
use crate::api::user::UserId;

#[derive(Insertable)]
#[table_name = "awards"]
pub struct AwardInput<'a> {
    pub evaluation_id: &'a str,
    pub award_name: &'a str,
    pub kind: &'a str,
    pub value: f64,
}

#[derive(Queryable, QueryableByName)]
pub struct AwardAchievementData {
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

pub struct AwardAchievement<'a> {
    context: &'a ApiContext<'a>,
    award: Award,
    data: AwardAchievementData,
}

impl AwardAchievement<'_> {
    /// Get the best score award for (user, problem)
    pub fn find_best<'a>(
        context: &'a ApiContext<'a>,
        award: &Award,
        user_id: &str,
        problem_name: &str,
    ) -> FieldResult<AwardAchievement<'a>> {
        let kind = match award.material.domain {
            AwardDomain::Score(_) => "SCORE",
            AwardDomain::Badge(_) => "BADGE",
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
            .unwrap_or(AwardAchievementData {
                evaluation_id: None,
                award_name: award.name.0.to_owned(),
                value: 0f64,
                kind: kind.to_owned(),
            });
        Ok(AwardAchievement {
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
    ) -> FieldResult<AwardAchievement<'a>> {
        let kind = match award.material.domain {
            AwardDomain::Score(_) => "SCORE",
            AwardDomain::Badge(_) => "BADGE",
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
            .unwrap_or(AwardAchievementData {
                evaluation_id: Some(evaluation_id.to_owned()),
                award_name: award.name.0.to_owned(),
                value: 0f64,
                kind: kind.to_owned(),
            });
        Ok(AwardAchievement {
            award: (*award).clone(),
            context,
            data,
        })
    }
}

#[juniper_ext::graphql]
impl AwardAchievement<'_> {
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

    pub fn grade(&self) -> AwardGrade {
        match self.award.material.domain.clone() {
            AwardDomain::Score(domain) => AwardGrade::Score(ScoreAwardGrade {
                domain,
                value: ScoreAwardValue {
                    score: Score(self.data.value),
                },
            }),
            AwardDomain::Badge(domain) => AwardGrade::Badge(BadgeAwardGrade {
                domain,
                value: BadgeAwardValue {
                    badge: self.data.value == 1f64,
                },
            }),
        }
    }
}

pub struct AwardView<'a> {
    pub problem: &'a Problem<'a>,
    pub award: Award,
    pub user_id: Option<UserId>,
}

#[juniper_ext::graphql]
impl<'a> AwardView<'a> {
    pub fn tackling(&self) -> Option<AwardTackling<'a>> {
        self.user_id.as_ref().map(|user_id| AwardTackling {
            problem: self.problem,
            award: self.award.clone(),
            user_id: (*user_id).clone(),
        })
    }

    pub fn name(&self) -> &AwardName {
        &self.award.name
    }

    pub fn material(&self) -> &AwardMaterial {
        &self.award.material
    }
}

pub struct AwardTackling<'a> {
    pub problem: &'a Problem<'a>,
    pub award: Award,
    pub user_id: UserId,
}

#[juniper_ext::graphql]
impl<'a> AwardTackling<'a> {
    pub fn best_achievement(&self) -> FieldResult<AwardAchievement<'a>> {
        Ok(AwardAchievement::find_best(
            &self.problem.context(),
            &self.award,
            &self.user_id.0,
            &self.problem.name().0,
        )?)
    }
}
