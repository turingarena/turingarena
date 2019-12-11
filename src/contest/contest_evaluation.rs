use std::error::Error;
use std::path::{Path, PathBuf};
use std::thread;

use diesel::prelude::*;
use diesel::sql_types::{Bool, Double, Text};
use juniper::FieldResult;

use api::{ApiConfig, ApiContext};
use award::*;
use award::{AwardInput, AwardOutcome};
use contest_problem::{Problem, ProblemData};
use contest_submission::{self, Submission};
use contest_submission::{SubmissionData, SubmissionId};
use evaluation::Event;
use problem::driver::ProblemDriver;
use schema::{evaluation_awards, evaluation_events, evaluations};

use super::super::award::{AwardName, Score};
use super::submission::FieldValue;
use super::*;

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
    context: &'a ApiContext<'a>,
    data: EvaluationData,
}

impl<'a> Evaluation<'a> {
    /// Evaluated submission
    pub fn submission(&self) -> FieldResult<Submission<'a>> {
        Submission::by_id(self.context, &self.data.submission_id)
    }

    /// Evaluation status
    pub fn status(&self) -> EvaluationStatus {
        EvaluationStatus::from(&self.data.status)
    }

    /// Evaluation awards
    pub fn awards(&self) -> FieldResult<Vec<AwardOutcome<'a>>> {
        AwardOutcome::of_evaluation(&self.context, &self.data.id)
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

    /// Gets the evaluation with the specified id from the database
    pub fn by_id<'b>(context: &'b ApiContext, id: &str) -> FieldResult<Evaluation<'b>> {
        let data = evaluations::table
            .filter(evaluations::dsl::id.eq(id))
            .first::<EvaluationData>(&context.database)?;
        Ok(Evaluation { context, data })
    }

    /// Gets the evaluation with the specified id from the database
    pub fn of_submission<'b>(
        context: &'b ApiContext,
        submission_id: &str,
    ) -> FieldResult<Evaluation<'b>> {
        let data = evaluations::table
            .filter(evaluations::dsl::submission_id.eq(submission_id))
            .first::<EvaluationData>(&context.database)?;
        Ok(Evaluation { context, data })
    }

    /// start the evaluation thread
    pub fn evaluate(submission: &Submission, config: &ApiConfig) -> QueryResult<()> {
        let config = config.clone();
        let submission_id = submission.id();

        thread::spawn(move || {
            let context = config.create_context(None);
            let evaluation = Evaluation::create(&context, submission_id);
            evaluation.run();
        });
        Ok(())
    }

    fn create(context: &'a ApiContext, submission_id: SubmissionId) -> Self {
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
        Evaluation::by_id(&context, &id).unwrap()
    }

    fn run(&self) {
        let field_values = self.load_submission_field_values();
        let problem_path = self.load_problem_path();

        let evaluation::Evaluation(receiver) =
            Self::do_evaluate(problem_path, submission::Submission { field_values });

        for (serial, event) in receiver.into_iter().enumerate() {
            self.save_awards(&event).unwrap();
            self.save_event(serial as i32, &event).unwrap();
        }

        self.set_status(EvaluationStatus::Success).unwrap();
    }

    fn load_submission_field_values(&self) -> Vec<FieldValue> {
        let submission = self.submission().unwrap();
        submission
            .files()
            .expect("Unable to load submission files")
            .into_iter()
            .map(|file| submission::FieldValue {
                field: submission::FieldId(file.field_id.clone()),
                file: submission::File {
                    name: submission::FileName(file.name.clone()),
                    content: file.content.clone(),
                },
            })
            .collect::<Vec<_>>()
    }

    fn load_problem_path(&self) -> PathBuf {
        let submission = self.submission().unwrap();
        let problem = Problem::by_name(&self.context, submission.problem_name()).unwrap();
        problem.unpack()
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
        if let Event::Score(score_event) = event {
            let score_award_input = AwardInput {
                kind: "SCORE",
                award_name: &score_event.award_name.0,
                value: score_event.score.0,
                evaluation_id: &self.data.id,
            };
            diesel::insert_into(evaluation_awards::table)
                .values(&score_award_input)
                .execute(&self.context.database)?;
        }
        if let Event::Badge(badge_event) = event {
            let badge_award_input = AwardInput {
                kind: "BADGE",
                award_name: &badge_event.award_name.0,
                value: if badge_event.badge { 1f64 } else { 0f64 },
                evaluation_id: &self.data.id,
            };
            diesel::insert_into(evaluation_awards::table)
                .values(&badge_award_input)
                .execute(&self.context.database)?;
        }
        Ok(())
    }

    #[cfg(feature = "task-maker")]
    fn do_evaluate<P: AsRef<Path>>(
        problem_path: P,
        submission: submission::Submission,
    ) -> evaluation::Evaluation {
        use task_maker::driver::IoiProblemDriver;
        IoiProblemDriver::evaluate(problem_path, submission)
    }

    #[cfg(not(feature = "task-maker"))]
    fn do_evaluate<P: AsRef<Path>>(
        problem_path: P,
        submission: submission::Submission,
    ) -> evaluation::Evaluation {
        unreachable!("Enable feature 'task-maker' to evaluate solutions")
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
pub struct EvaluationData {
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
