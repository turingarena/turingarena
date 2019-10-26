use crate::schema::{evaluation_events, scorables};
use crate::submission::{self, Submission, SubmissionStatus};
use diesel::prelude::*;
use diesel::sql_types::{Double, Text};
use juniper::FieldResult;
use std::error::Error;
use std::thread;
use turingarena::evaluation::mem::Evaluation;
use turingarena::evaluation::Event;
use turingarena::problem::driver::{ProblemDriver, ProblemPack};
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

#[derive(Queryable)]
pub struct ScorableResult {
    /// Id of the submission  
    #[allow(dead_code)]
    submission_id: String,

    /// Id of the scorable
    scorable_id: String,

    /// Score of the submission
    score: f64,
}

#[juniper::object]
impl ScorableResult {
    /// The score
    fn score(&self) -> Score {
        Score(self.score)
    }

    /// Id of the scorable
    fn scorable_id(&self) -> &String {
        &self.scorable_id
    }
}

#[derive(QueryableByName)]
pub struct MaxScore {
    #[sql_type = "Text"]
    scorable_id: String,

    #[sql_type = "Double"]
    score: f64,

    #[sql_type = "Text"]
    submission_id: String,
}

/// Maximum score
#[juniper::object]
impl MaxScore {
    /// Id of the most recent submission that made the max score
    fn submission_id(&self) -> &String {
        &self.submission_id
    }

    /// The score
    fn score(&self) -> Score {
        Score(self.score)
    }

    /// Id of the scorable
    fn scorable_id(&self) -> &String {
        &self.scorable_id
    }
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
    submission_id: &str,
) -> QueryResult<Vec<EvaluationEvent>> {
    evaluation_events::table
        .filter(evaluation_events::dsl::submission_id.eq(submission_id))
        .load(conn)
}

/// Get the scorable for (user, problem)
pub fn query_scorables_of_user_and_problem(
    conn: &SqliteConnection,
    user_id: &str,
    problem_name: &str,
) -> QueryResult<Vec<MaxScore>> {
    diesel::sql_query(
        "
        SELECT sc.scorable_id, MAX(sc.score) as score, (
            SELECT s.id
            FROM submissions s JOIN scorables sci ON s.id = sci.submission_id
            WHERE sci.score = score AND sci.scorable_id = sc.scorable_id
            ORDER BY s.created_at DESC
            LIMIT 1
        ) as submission_id
        FROM scorables sc JOIN submissions s ON sc.submission_id = s.id
        WHERE s.problem_name = ? AND s.user_id = ?
        GROUP BY sc.scorable_id
    ",
    )
    .bind::<Text, _>(problem_name)
    .bind::<Text, _>(user_id)
    .load::<MaxScore>(conn)
}

/// Get the scorable of (user, problem, submission)
pub fn query_scorables(
    conn: &SqliteConnection,
    submission_id: &str,
) -> QueryResult<Vec<ScorableResult>> {
    scorables::table
        .filter(scorables::dsl::submission_id.eq(submission_id))
        .load(conn)
}

/// start the evaluation thread
pub fn evaluate(
    problem_pack: ProblemPack,
    submission: &Submission,
    db_connection: SqliteConnection,
) -> QueryResult<()> {
    let submission_id = submission.id.clone();
    let submission = submission.to_mem_submission(&db_connection)?;
    thread::spawn(move || {
        let Evaluation(receiver) = IoiProblemDriver::evaluate(problem_pack, submission);
        for (serial, event) in receiver.into_iter().enumerate() {
            insert_event(&db_connection, serial as i32, &submission_id, &event).unwrap();
        }
        submission::set_status(&db_connection, &submission_id, SubmissionStatus::Success).unwrap();
    });
    Ok(())
}
