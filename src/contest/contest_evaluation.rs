use std::error::Error;
use std::thread;

use diesel::prelude::*;
use diesel::sql_types::{Bool, Double, Text};
use juniper::FieldResult;

use super::super::award::{AwardName, Score};
use super::*;
use crate::contest::api::{ApiConfig, ApiContext};
use crate::contest::award::AwardInput;
use crate::contest::contest_problem::ProblemData;
use crate::contest::contest_submission::SubmissionData;
use award::*;
use contest_submission::{self, Submission, SubmissionStatus};
use evaluation::{Evaluation, Event};
use problem::driver::ProblemDriver;
use schema::{awards, evaluation_events};
use std::path::{Path, PathBuf};

/// An evaluation event
#[derive(Queryable, Serialize, Deserialize, Clone, Debug)]
pub struct EvaluationEvent {
    /// id of the submission
    submission_id: String,

    /// serial number of the event
    serial: i32,

    /// value of the event, serialized
    event_json: String,
}

#[juniper::object]
impl EvaluationEvent {
    /// serial number of the event
    fn serial(&self) -> i32 {
        self.serial
    }

    /// value of this evaluation event
    fn event(&self) -> FieldResult<Event> {
        Ok(serde_json::from_str(&self.event_json)?)
    }

    /// events as JSON format
    /// This is currently provided only as a woraround the fact that
    /// events doesn't work, and should be removed in the future!
    fn event_json(&self) -> &String {
        &self.event_json
    }
}

impl EvaluationEvent {
    pub fn insert(
        context: &ApiContext,
        serial: i32,
        submission_id: &str,
        event: &Event,
    ) -> FieldResult<()> {
        if let Event::Score(score_event) = event {
            let score_award_input = AwardInput {
                kind: "SCORE",
                award_name: &score_event.award_name.0,
                value: score_event.score.0,
                submission_id,
            };
            diesel::insert_into(awards::table)
                .values(&score_award_input)
                .execute(&context.database)?;
        }
        if let Event::Badge(badge_event) = event {
            let badge_award_input = AwardInput {
                kind: "BADGE",
                award_name: &badge_event.award_name.0,
                value: if badge_event.badge { 1f64 } else { 0f64 },
                submission_id,
            };
            diesel::insert_into(awards::table)
                .values(&badge_award_input)
                .execute(&context.database)?;
        }
        let event_input = EvaluationEventInput {
            serial,
            submission_id,
            event_json: serde_json::to_string(event)?,
        };
        diesel::insert_into(evaluation_events::table)
            .values(&event_input)
            .execute(&context.database)?;
        Ok(())
    }

    /// return a list of evaluation events for the specified evaluation
    pub fn of_submission(
        context: &ApiContext,
        submission_id: &str,
    ) -> FieldResult<Vec<EvaluationEvent>> {
        Ok(evaluation_events::table
            .filter(evaluation_events::dsl::submission_id.eq(submission_id))
            .load(&context.database)?)
    }
}

#[derive(Insertable)]
#[table_name = "evaluation_events"]
struct EvaluationEventInput<'a> {
    submission_id: &'a str,
    serial: i32,
    event_json: String,
}

/// start the evaluation thread
pub fn evaluate<P: AsRef<Path>>(
    problem_path: P,
    submission: &Submission,
    config: &ApiConfig,
) -> QueryResult<()> {
    let config = config.clone();
    let submission_data = submission.data().clone();
    let problem_path = problem_path.as_ref().to_owned();

    thread::spawn(move || {
        let context = config.create_context(None);
        let submission = Submission::new(&context, submission_data);

        let mut field_values = Vec::new();
        let files = submission.files().expect("Unable to load submission files");
        for file in files {
            field_values.push(submission::FieldValue {
                field: submission::FieldId(file.field_id.clone()),
                file: submission::File {
                    name: submission::FileName(file.name.clone()),
                    content: file.content.clone(),
                },
            })
        }

        let Evaluation(receiver) =
            do_evaluate(problem_path, submission::Submission { field_values });
        for (serial, event) in receiver.into_iter().enumerate() {
            EvaluationEvent::insert(&context, serial as i32, &submission.id().0, &event).unwrap();
        }
        submission.set_status(SubmissionStatus::Success).unwrap();
    });
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
