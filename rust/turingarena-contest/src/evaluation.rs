use crate::problem::ContestProblem;
use crate::schema::evaluation_events;
use crate::submission::Submission;
use diesel::prelude::*;
use juniper::FieldResult;
use std::error::Error;
use std::thread;
use turingarena::evaluation::mem::Evaluation;
use turingarena::evaluation::Event;
use turingarena::problem::driver::ProblemDriver;
use turingarena_task_maker::driver::IoiProblemDriver;

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

#[derive(Insertable)]
#[table_name = "evaluation_events"]
struct EvaluationEventInput<'a> {
    submission_id: &'a str,
    serial: i32,
    event_json: String,
}

fn insert_event(
    conn: &SqliteConnection,
    serial: i32,
    submission_id: &str,
    event: &Event,
) -> Result<(), Box<dyn Error>> {
    let event_input = EvaluationEventInput {
        serial,
        submission_id,
        event_json: serde_json::to_string(event)?,
    };
    diesel::insert_into(evaluation_events::table)
        .values(&event_input)
        .execute(conn)?;
    Ok(())
}

/// return a list of evaluation events for the specified evaluation
pub fn query_events(
    conn: &SqliteConnection,
    submission_id: String,
) -> QueryResult<Vec<EvaluationEvent>> {
    evaluation_events::table
        .filter(evaluation_events::dsl::submission_id.eq(submission_id))
        .load(conn)
}

/// start the evaluation thread
pub fn evaluate(
    problem: &ContestProblem,
    submission: &Submission,
    db_connection: SqliteConnection,
) {
    let pack = problem.pack();
    let submission_id = submission.id.clone();
    let submission = submission.to_mem_submission();
    thread::spawn(move || {
        let Evaluation(receiver) = IoiProblemDriver::evaluate(pack, submission);
        let mut serial = 0;
        for event in receiver {
            insert_event(&db_connection, serial, &submission_id, &event).unwrap();
            serial = serial + 1;
        }
    });
}
