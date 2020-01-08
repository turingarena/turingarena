use std::path::PathBuf;
use std::thread;

use diesel::prelude::*;

use juniper::FieldResult;

use root::{ApiConfig, ApiContext};

use award::{AwardAchievement, AwardInput};
use contest_problem::Problem;
use contest_submission::SubmissionId;
use contest_submission::{self, Submission};
use evaluation::Event;
use schema::{awards, evaluation_events, evaluations};

use crate::award::{AwardValue, BadgeAwardValue, ScoreAwardValue};
use crate::evaluation::AwardEvent;

use super::submission::FieldValue;
use super::*;
use crate::api::award::{AwardGrading, ScoreAwardGrading};
use crate::data::award::{Award, Score, ScoreAwardDomain, ScoreAwardGrade};

/// An evaluation event
#[derive(Queryable, Serialize, Deserialize, Clone, Debug)]
struct EvaluationEvent {
    /// Value of the event, serialized
    pub event_json: String,
}

#[derive(Insertable)]
#[table_name = "evaluation_events"]
struct EvaluationEventInput<'a> {
    evaluation_id: &'a str,
    serial: i32,
    event_json: String,
}

pub struct Evaluation<'a> {
    context: &'a ApiContext,
    data: EvaluationData,
}

#[juniper_ext::graphql(Context = ApiContext)]
impl<'a> Evaluation<'a> {
    pub fn id(&self) -> &str {
        &self.data.id
    }

    /// Evaluated submission
    pub fn submission(&self) -> FieldResult<Submission<'a>> {
        Submission::by_id(self.context, &self.data.submission_id)
    }

    /// Evaluation status
    pub fn status(&self) -> EvaluationStatus {
        EvaluationStatus::from(&self.data.status)
    }

    /// Evaluation result (achievements, scores, etc.)
    pub fn result(&self) -> Option<EvaluationResult> {
        match self.status() {
            EvaluationStatus::Success => Some(EvaluationResult { evaluation: &self }),
            _ => None,
        }
    }

    pub fn score_domain(&self) -> FieldResult<ScoreAwardDomain> {
        Ok(self.submission()?.problem()?.score_domain())
    }

    pub fn grading(&self) -> FieldResult<ScoreAwardGrading> {
        let grade = match self.result() {
            Some(result) => Some(result.grade()?),
            None => None,
        };
        Ok(ScoreAwardGrading {
            domain: self.score_domain()?,
            grade,
        })
    }

    pub fn awards(&self) -> FieldResult<Vec<EvaluationAward>> {
        let result = self.result();

        self.submission()?
            .problem()?
            .material()
            .awards
            .iter()
            .map(|award| -> FieldResult<_> {
                // FIXME: logic is quite ugly here, refactor
                let achievement = if result.is_some() {
                    Some(AwardAchievement::find(&self.context, award, self.id())?)
                } else {
                    None
                };
                Ok(EvaluationAward {
                    award: (*award).clone(),
                    evaluation: &self,
                    achievement,
                })
            })
            .collect::<FieldResult<Vec<_>>>()
    }

    /// Evaluation events of this submission
    pub fn events(&self) -> FieldResult<Vec<Event>> {
        Ok(evaluation_events::table
            .select(evaluation_events::dsl::event_json)
            .filter(evaluation_events::dsl::evaluation_id.eq(&self.data.id))
            .order(evaluation_events::dsl::serial)
            .load::<String>(&self.context.database)?
            .into_iter()
            .map(|json| serde_json::from_str(&json))
            .collect::<std::result::Result<_, _>>()?)
    }
}

impl<'a> Evaluation<'a> {
    pub fn by_id(context: &'a ApiContext, id: &str) -> FieldResult<Self> {
        let data = evaluations::table
            .find(id)
            .first::<EvaluationData>(&context.database)?;
        Ok(Evaluation { context, data })
    }

    pub fn list(context: &'a ApiContext) -> FieldResult<Vec<Self>> {
        Ok(evaluations::table
            .load::<EvaluationData>(&context.database)?
            .into_iter()
            .map(|data| Evaluation { context, data })
            .collect())
    }

    pub fn of_submission<'b>(
        context: &'b ApiContext,
        submission_id: &str,
    ) -> FieldResult<Evaluation<'b>> {
        let data = evaluations::table
            .filter(evaluations::dsl::submission_id.eq(submission_id))
            .order_by(evaluations::dsl::created_at.desc())
            .first::<EvaluationData>(&context.database)?;
        Ok(Evaluation { context, data })
    }

    /// start the evaluation thread
    pub fn start_new(submission: &Submission, config: &ApiConfig) -> QueryResult<()> {
        let config = config.clone();
        let submission_id = submission.id();

        thread::spawn(move || {
            let context = config.create_context(None);
            let evaluation =
                Evaluation::create(&context, submission_id).expect("Unable to create evaluation");
            evaluation.run().expect("Unable to run evaluation");
        });
        Ok(())
    }

    fn create(context: &'a ApiContext, submission_id: SubmissionId) -> FieldResult<Self> {
        let id = uuid::Uuid::new_v4().to_string();
        let created_at = chrono::Local::now().to_rfc3339();

        diesel::insert_into(evaluations::table)
            .values(&EvaluationInsertable {
                id: &id,
                submission_id: &submission_id.0,
                created_at: &created_at,
                status: &EvaluationStatus::Pending.to_string(),
            })
            .execute(&context.database)
            .expect("Unable to insert evaluation");
        Ok(Evaluation::by_id(&context, &id)?)
    }

    fn run(&self) -> FieldResult<()> {
        let field_values = self.load_submission_field_values()?;
        let problem_path = self.load_problem_path()?;

        let submission = submission::Submission { field_values };
        let receiver = task_maker::evaluate(problem_path, submission)?;

        for (serial, event) in receiver.into_iter().enumerate() {
            self.save_awards(&event)?;
            self.save_event(serial as i32, &event)?;
        }

        self.set_status(EvaluationStatus::Success)?;

        Ok(())
    }

    fn load_submission_field_values(&self) -> FieldResult<Vec<FieldValue>> {
        let submission = self.submission()?;
        Ok(submission.field_values()?)
    }

    fn load_problem_path(&self) -> FieldResult<PathBuf> {
        let submission = self.submission()?;
        let problem = Problem::by_name(&self.context, submission.problem_name())?;
        Ok(problem.unpack()?)
    }

    fn set_status(&self, status: EvaluationStatus) -> FieldResult<()> {
        diesel::update(evaluations::table)
            .filter(evaluations::dsl::id.eq(&self.data.id))
            .set(evaluations::dsl::status.eq(status.to_string()))
            .execute(&self.context.database)?;
        Ok(())
    }

    fn save_event(&self, serial: i32, event: &Event) -> FieldResult<()> {
        let event_input = EvaluationEventInput {
            serial,
            evaluation_id: &self.data.id,
            event_json: serde_json::to_string(event)?,
        };
        diesel::insert_into(evaluation_events::table)
            .values(&event_input)
            .execute(&self.context.database)?;
        Ok(())
    }

    fn save_awards(&self, event: &Event) -> FieldResult<()> {
        if let Event::Award(AwardEvent { award_name, value }) = event {
            let score_award_input = AwardInput {
                kind: match value {
                    AwardValue::Score(_) => "SCORE",
                    AwardValue::Badge(_) => "BADGE",
                },
                award_name: &award_name.0,
                value: match value {
                    AwardValue::Score(ScoreAwardValue { score }) => score.0,
                    AwardValue::Badge(BadgeAwardValue { badge }) => {
                        if *badge {
                            1f64
                        } else {
                            0f64
                        }
                    }
                },
                evaluation_id: &self.data.id,
            };
            diesel::insert_into(awards::table)
                .values(&score_award_input)
                .execute(&self.context.database)?;
        }
        Ok(())
    }
}

#[derive(Insertable)]
#[table_name = "evaluations"]
struct EvaluationInsertable<'a> {
    id: &'a str,
    submission_id: &'a str,
    created_at: &'a str,
    status: &'a str,
}

#[derive(Queryable, Clone)]
struct EvaluationData {
    /// ID of the evaluation, that is a random generated UUID
    id: String,

    /// ID of the evaluated submission
    submission_id: String,

    /// Time at which evaluation was started
    created_at: String,

    /// Submission status
    status: String,
}

/// Status of an evaluation
#[derive(Copy, Clone, juniper::GraphQLEnum)]
pub enum EvaluationStatus {
    /// The submission is in the process of evaluation by the server
    Pending,

    /// The evaluation process terminated correctly
    Success,

    /// The evaluation process crashed with an error
    Failed,
}

impl EvaluationStatus {
    fn from(value: &str) -> Self {
        match value {
            "PENDING" => EvaluationStatus::Pending,
            "SUCCESS" => EvaluationStatus::Success,
            "FAILED" => EvaluationStatus::Failed,
            _ => unreachable!("Corrupted db"),
        }
    }

    fn to_string(self) -> String {
        match self {
            EvaluationStatus::Pending => "PENDING",
            EvaluationStatus::Success => "SUCCESS",
            EvaluationStatus::Failed => "FAILED",
        }
        .to_owned()
    }
}

pub struct EvaluationAward<'a> {
    pub evaluation: &'a Evaluation<'a>,
    pub achievement: Option<AwardAchievement<'a>>,
    pub award: Award,
}

#[juniper_ext::graphql(Context = ApiContext)]
impl EvaluationAward<'_> {
    pub fn grading(&self) -> FieldResult<AwardGrading> {
        Ok(AwardGrading::from(
            self.award.material.domain.clone(),
            self.achievement.as_ref().map(|a| a.grade()),
        ))
    }
}

pub struct EvaluationResult<'a> {
    pub evaluation: &'a Evaluation<'a>,
}

#[juniper_ext::graphql(Context = ApiContext)]
impl EvaluationResult<'_> {
    /// Award achievement of this evaluation
    pub fn achievements(&self) -> FieldResult<Vec<AwardAchievement>> {
        self.evaluation
            .submission()?
            .problem()?
            .material()
            .awards
            .iter()
            .map(|award| {
                AwardAchievement::find(&self.evaluation.context, award, self.evaluation.id())
            })
            .collect::<FieldResult<Vec<_>>>()
    }

    /// Sum of the score awards
    pub fn score(&self) -> FieldResult<ScoreAwardValue> {
        Ok(ScoreAwardValue::total(
            self.achievements()?
                .into_iter()
                .map(|achievement| achievement.value())
                .filter_map(|value| match value {
                    AwardValue::Score(value) => Some(value),
                    _ => None,
                })
                .collect::<Vec<_>>(),
        ))
    }

    pub fn grade(&self) -> FieldResult<ScoreAwardGrade> {
        Ok(ScoreAwardGrade {
            domain: self.evaluation.submission()?.problem()?.score_domain(),
            value: self.score()?,
        })
    }
}
