use crate::problem::ContestProblem;
use crate::schema::evaluation_events;
use crate::submission::Submission;
use diesel::prelude::*;
use std::error::Error;
use std::thread;
use turingarena::evaluation::mem::Evaluation;
use turingarena::evaluation::Event;
use turingarena::problem::driver::ProblemDriver;
use turingarena_task_maker::driver::IoiProblemDriver;

/// An evaluation event
#[derive(Queryable, Serialize, Deserialize, Clone, Debug)]
struct EvaluationEvent {
    /// id of the submission
    submission_id: String,

    /// serial number of the event
    serial: i32,

    /// value of the event, serialized
    value_json: String,
}

#[derive(Insertable)]
#[table_name = "evaluation_events"]
struct EvaluationEventInput<'a> {
    submission_id: &'a str,
    serial: i32,
    value_json: String,
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
        value_json: serde_json::to_string(event)?,
    };
    diesel::insert_into(evaluation_events::table)
        .values(&event_input)
        .execute(conn)?;
    Ok(())
}

/// start the evaluation thread
pub fn evaluate(problem: &ContestProblem, submission: &Submission) {
    let pack = problem.pack();
    let submission_id = submission.id.clone();
    let submission = submission.to_mem_submission();
    thread::spawn(move || {
        let conn = crate::db_connect().unwrap();
        let Evaluation(receiver) = IoiProblemDriver::evaluate(pack, submission);
        let mut serial = 0;
        for event in receiver {
            insert_event(&conn, serial, &submission_id, &event).unwrap();
            serial = serial + 1;
        }
    });
}
