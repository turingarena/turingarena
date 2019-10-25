use crate::problem::ContestProblem;
use crate::schema::{evaluation_events, scorables};
use crate::submission::Submission;
use diesel::prelude::*;
use diesel::query_dsl::LoadQuery;
use diesel::sql_types::{Double, Text};
use juniper::FieldResult;
use std::error::Error;
use std::thread;
use turingarena::evaluation::mem::Evaluation;
use turingarena::evaluation::{Event, ScoreEvent};
use turingarena::problem::driver::ProblemDriver;
use turingarena::score::Score;
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

#[derive(Insertable)]
#[table_name = "scorables"]
struct ScorableInput<'a> {
    submission_id: &'a str,
    scorable_id: &'a str,
    score: f64,
}

#[derive(QueryableByName)]
struct Scorable {
    #[sql_type = "Text"]
    scorable_id: String,

    #[sql_type = "Double"]
    score: f64,
}

fn insert_event(
    conn: &SqliteConnection,
    serial: i32,
    submission_id: &str,
    event: &Event,
) -> Result<(), Box<dyn Error>> {
    if let Event::Score(score_event) = event {
        let scorable_input = ScorableInput {
            scorable_id: &score_event.scorable_id,
            score: score_event.score.0,
            submission_id,
        };
        diesel::insert_into(scorables::table)
            .values(&scorable_input)
            .execute(conn)?;
    }
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
pub fn query_scorables_of_user_and_problem(
    conn: &SqliteConnection,
    user_id: &str,
    problem_name: &str,
) -> QueryResult<Vec<ScoreEvent>> {
    Ok(diesel::sql_query(
        "
        SELECT sc.scorable_id, MAX(sc.score) as score
        FROM scorables sc JOIN submissions s ON sc.submission_id = s.id
        WHERE s.problem_name = ? AND s.user_id = ?
        GROUP BY sc.scorable_id
    ",
    )
    .bind::<Text, _>(problem_name)
    .bind::<Text, _>(user_id)
    .load::<Scorable>(conn)?
    .into_iter()
    .map(|e| ScoreEvent {
        scorable_id: e.scorable_id,
        score: Score(e.score),
    })
    .collect())
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
