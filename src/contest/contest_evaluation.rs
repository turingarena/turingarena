use std::error::Error;
use std::thread;

use diesel::prelude::*;
use diesel::sql_types::{Bool, Double, Text};
use juniper::FieldResult;

use super::*;
use crate::contest::api::{ApiConfig, ApiContext};
use crate::contest::contest_problem::ProblemData;
use crate::contest::contest_submission::{submission_files, SubmissionData};
use award::{AwardName, Score};
use contest_submission::{self, Submission, SubmissionStatus};
use evaluation::{Evaluation, Event};
use problem::driver::ProblemDriver;
use schema::{badge_awards, evaluation_events, score_awards};
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

#[derive(Insertable)]
#[table_name = "evaluation_events"]
struct EvaluationEventInput<'a> {
    submission_id: &'a str,
    serial: i32,
    event_json: String,
}

#[derive(Insertable)]
#[table_name = "score_awards"]
struct ScoreAwardInput<'a> {
    submission_id: &'a str,
    award_name: &'a str,
    score: f64,
}

#[derive(Insertable)]
#[table_name = "badge_awards"]
struct BadgeAwardInput<'a> {
    submission_id: &'a str,
    award_name: &'a str,
    badge: bool,
}

#[derive(Queryable)]
pub struct ScoreAward {
    /// Id of the submission  
    #[allow(dead_code)]
    submission_id: String,

    /// Name of the award
    award_name: String,

    /// Score of the submission
    score: f64,
}

#[derive(Queryable)]
pub struct BadgeAward {
    /// Id of the submission
    #[allow(dead_code)]
    submission_id: String,

    /// Name of the award
    award_name: String,

    /// Score of the submission
    badge: bool,
}

#[juniper::object]
impl ScoreAward {
    /// The score
    fn score(&self) -> Score {
        Score(self.score)
    }

    /// Name of the award
    fn award_name(&self) -> AwardName {
        AwardName(self.award_name.clone())
    }
}

#[juniper::object]
impl BadgeAward {
    /// The badge
    fn badge(&self) -> bool {
        self.badge
    }

    /// Name of the award
    fn award_name(&self) -> AwardName {
        AwardName(self.award_name.clone())
    }
}

#[derive(QueryableByName)]
pub struct MaxScoreAward {
    #[sql_type = "Text"]
    award_name: String,

    #[sql_type = "Double"]
    score: f64,

    #[sql_type = "Text"]
    submission_id: String,
}

#[derive(QueryableByName)]
pub struct BestBadgeAward {
    #[sql_type = "Text"]
    award_name: String,

    #[sql_type = "Bool"]
    badge: bool,

    #[sql_type = "Text"]
    submission_id: String,
}

/// Maximum score award
#[juniper::object]
impl MaxScoreAward {
    /// Id of the most recent submission that made the max score
    fn submission_id(&self) -> &String {
        &self.submission_id
    }

    /// The score
    fn score(&self) -> Score {
        Score(self.score)
    }

    /// Name of the award
    fn award_name(&self) -> &String {
        &self.award_name
    }
}

/// Beste badge award
#[juniper::object]
impl BestBadgeAward {
    /// Id of the most recent submission that made the max score
    fn submission_id(&self) -> &String {
        &self.submission_id
    }

    /// The score
    fn badge(&self) -> bool {
        self.badge
    }

    /// Name of the award
    fn award_name(&self) -> &String {
        &self.award_name
    }
}

fn insert_event(
    conn: &SqliteConnection,
    serial: i32,
    submission_id: &str,
    event: &Event,
) -> Result<()> {
    if let Event::Score(score_event) = event {
        let score_award_input = ScoreAwardInput {
            award_name: &score_event.award_name.0,
            score: score_event.score.0,
            submission_id,
        };
        diesel::insert_into(score_awards::table)
            .values(&score_award_input)
            .execute(conn)?;
    }
    if let Event::Badge(badge_event) = event {
        let badge_award_input = BadgeAwardInput {
            award_name: &badge_event.award_name.0,
            badge: badge_event.badge,
            submission_id,
        };
        diesel::insert_into(badge_awards::table)
            .values(&badge_award_input)
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

/// Get the best score award for (user, problem)
pub fn query_score_awards_of_user_and_problem(
    conn: &SqliteConnection,
    user_id: &str,
    problem_name: &str,
) -> QueryResult<Vec<MaxScoreAward>> {
    diesel::sql_query(
        "
        SELECT sc.award_name, MAX(sc.score) as score, (
            SELECT s.id
            FROM submissions s JOIN score_awards sci ON s.id = sci.submission_id
            WHERE sci.score = score AND sci.award_name = sc.award_name
            ORDER BY s.created_at DESC
            LIMIT 1
        ) as submission_id
        FROM score_awards sc JOIN submissions s ON sc.submission_id = s.id
        WHERE s.problem_name = ? AND s.user_id = ?
        GROUP BY sc.award_name
    ",
    )
    .bind::<Text, _>(problem_name)
    .bind::<Text, _>(user_id)
    .load::<MaxScoreAward>(conn)
}

/// Get the best award badge for (user, problem)
pub fn query_badge_awards_of_user_and_problem(
    conn: &SqliteConnection,
    user_id: &str,
    problem_name: &str,
) -> QueryResult<Vec<BestBadgeAward>> {
    diesel::sql_query(
        "
        SELECT sc.award_name, MAX(sc.badge) as badge, (
            SELECT s.id
            FROM submissions s JOIN badge_awards sci ON s.id = sci.submission_id
            WHERE sci.badge = badge AND sci.award_name = sc.award_name
            ORDER BY s.created_at DESC
            LIMIT 1
        ) as submission_id
        FROM badge_awards sc JOIN submissions s ON sc.submission_id = s.id
        WHERE s.problem_name = ? AND s.user_id = ?
        GROUP BY sc.award_name
    ",
    )
    .bind::<Text, _>(problem_name)
    .bind::<Text, _>(user_id)
    .load::<BestBadgeAward>(conn)
}

/// Get the score awards of (user, problem, submission)
pub fn query_score_awards(
    conn: &SqliteConnection,
    submission_id: &str,
) -> QueryResult<Vec<ScoreAward>> {
    score_awards::table
        .filter(score_awards::dsl::submission_id.eq(submission_id))
        .load(conn)
}

/// Get the badge awards of (user, problem, submission)
pub fn query_badge_awards(
    conn: &SqliteConnection,
    submission_id: &str,
) -> QueryResult<Vec<BadgeAward>> {
    badge_awards::table
        .filter(badge_awards::dsl::submission_id.eq(submission_id))
        .load(conn)
}

/// start the evaluation thread
pub fn evaluate<P: AsRef<Path>>(
    problem_path: P,
    submission_data: &SubmissionData,
    config: &ApiConfig,
) -> QueryResult<()> {
    let config = config.clone();
    let submission_data = submission_data.clone();
    let problem_path = problem_path.as_ref().to_owned();
    thread::spawn(move || {
        let context = config.create_context(None);

        let mut field_values = Vec::new();
        let files = submission_files(&context.database, &submission_data.id)
            .expect("Unable to load submission files");
        for file in files {
            field_values.push(submission::FieldValue {
                field: submission::FieldId(file.field_id.clone()),
                file: submission::File {
                    name: submission::FileName(file.name.clone()),
                    content: file.content.clone(),
                },
            })
        }

        let submission = submission::Submission { field_values };

        let Evaluation(receiver) = do_evaluate(problem_path, submission);
        for (serial, event) in receiver.into_iter().enumerate() {
            insert_event(
                &context.database,
                serial as i32,
                &submission_data.id,
                &event,
            )
            .unwrap();
        }
        contest_submission::set_status(
            &context.database,
            &submission_data.id,
            SubmissionStatus::Success,
        )
        .unwrap();
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
