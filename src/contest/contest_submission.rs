use super::*;

use crate::contest::award::AwardOutcome;
use crate::contest::contest::ContestView;
use crate::contest::contest_evaluation::EvaluationStatus;
use crate::contest::user::UserId;
use api::ApiContext;
use award::*;
use diesel::{ExpressionMethods, QueryDsl, QueryResult, RunQueryDsl, SqliteConnection};
use juniper::FieldResult;
use juniper_ext::*;
use schema::{submission_files, submissions};
use crate::evaluation::Event;

/// Wraps a String that identifies a submission
#[derive(GraphQLNewtype)]
pub struct SubmissionId(pub String);

/// File of a submission. (submission_id, field_id) is the primary key
#[derive(Queryable)]
#[allow(dead_code)]
pub struct SubmissionFile {
    /// id of the submmission
    pub submission_id: String,

    /// id of the field in the sumbission form
    pub field_id: String,

    /// type of the file (e.g MIME text/plain)
    pub type_id: String,

    /// name of the file, as uploaded by the user (ex. solution.cpp)
    pub name: String,

    /// content of the file as bytes
    pub content: Vec<u8>,
}

#[juniper::object]
impl SubmissionFile {
    /// id of the submission
    fn field_id(&self) -> &String {
        &self.field_id
    }

    /// type of the file
    fn type_id(&self) -> &String {
        &self.type_id
    }

    /// name of the file
    fn name(&self) -> &String {
        &self.name
    }

    /// content of the file in base64 format
    fn content_base64(&self) -> String {
        base64::encode(&self.content)
    }
}

/// A submission in the database
#[derive(Queryable, Clone)]
pub struct SubmissionData {
    /// id of the submission, that is a random generated UUID
    id: String,

    /// id of user who made submission
    user_id: String,

    /// name of problem wich the submission refers to
    problem_name: String,

    /// time in wich the submission was created, saved as a RFC3339 date
    created_at: String,
}

pub struct Submission<'a> {
    context: &'a ApiContext<'a>,
    pub data: SubmissionData,
}

impl Submission<'_> {
    pub fn new<'a>(context: &'a ApiContext, data: SubmissionData) -> Submission<'a> {
        Submission { context, data }
    }

    pub fn data(&self) -> &SubmissionData {
        &self.data
    }

    pub fn evaluation(&self) -> FieldResult<contest_evaluation::Evaluation> {
        contest_evaluation::Evaluation::of_submission(self.context, &self.data.id)
    }

    /// Gets the submission with the specified id from the database
    pub fn by_id<'a>(context: &'a ApiContext, submission_id: &str) -> FieldResult<Submission<'a>> {
        let data = submissions::table
            .filter(submissions::dsl::id.eq(submission_id))
            .first::<SubmissionData>(&context.database)?;
        Ok(Submission { context, data })
    }

    /// Insert a new submission into the database, returning a submission object
    pub fn insert<'a>(
        context: &'a ApiContext,
        user_id: &str,
        problem_name: &str,
        files: Vec<FileInput>,
    ) -> FieldResult<Submission<'a>> {
        let id = uuid::Uuid::new_v4().to_string();
        let created_at = chrono::Local::now().to_rfc3339();
        let submission = SubmissionTableInput {
            id: &id,
            user_id,
            problem_name,
            created_at: &created_at,
        };
        diesel::insert_into(submissions::table)
            .values(submission)
            .execute(&context.database)?;
        for file in files {
            let submission_file = SubmissionFileTableInput {
                submission_id: &id,
                field_id: &file.field_id,
                type_id: &file.type_id,
                name: &file.name,
                content: &base64::decode(&file.content_base64)?,
            };
            diesel::insert_into(submission_files::table)
                .values(submission_file)
                .execute(&context.database)?;
        }
        Ok(Self::by_id(context, &id)?)
    }

    /// Gets all the submissions of the specified user
    pub fn by_user_and_problem<'a>(
        context: &'a ApiContext,
        user_id: &str,
        problem_name: &str,
    ) -> FieldResult<Vec<Submission<'a>>> {
        Ok(submissions::table
            .filter(submissions::dsl::user_id.eq(user_id))
            .filter(submissions::dsl::problem_name.eq(problem_name))
            .load::<SubmissionData>(&context.database)?
            .into_iter()
            .map(|data| contest_submission::Submission { context, data })
            .collect())
    }
}

#[juniper_ext::graphql]
impl Submission<'_> {
    /// UUID of the submission
    pub fn id(&self) -> SubmissionId {
        SubmissionId(self.data.id.clone())
    }

    /// Id of the user who made the submission
    pub fn user_id(&self) -> UserId {
        UserId(self.data.user_id.clone())
    }

    /// Name of the problem wich the submission refers to
    pub fn problem_name(&self) -> &String {
        &self.data.problem_name
    }

    /// Time at wich the submission was created
    pub fn created_at(&self) -> &String {
        &self.data.created_at
    }

    /// List of files of this submission
    pub fn files(&self) -> FieldResult<Vec<SubmissionFile>> {
        Ok(submission_files::table
            .filter(submission_files::dsl::submission_id.eq(&self.data.id))
            .load::<SubmissionFile>(&self.context.database)?)
    }

    /// Submission status
    pub fn status(&self) -> FieldResult<EvaluationStatus> {
        Ok(self.evaluation()?.status())
    }

    /// Scores of this submission
    pub fn awards(&self) -> FieldResult<Vec<AwardOutcome>> {
        self.evaluation()?.awards()
    }

    /// Evaluation events of this submission
    pub fn evaluation_events(&self) -> FieldResult<Vec<Event>> {
        self.evaluation()?.events()
    }
}

/// Input file for a submission file
#[derive(juniper::GraphQLInputObject)]
pub struct FileInput {
    /// type of the file submitted
    type_id: String,

    /// name of the field that this file refears to
    field_id: String,

    /// filename as uploaded by the user
    name: String,

    /// content of the file codified in base64
    content_base64: String,
}

#[derive(Insertable)]
#[table_name = "submissions"]
struct SubmissionTableInput<'a> {
    id: &'a str,
    user_id: &'a str,
    problem_name: &'a str,
    created_at: &'a str,
}

#[derive(Insertable)]
#[table_name = "submission_files"]
struct SubmissionFileTableInput<'a> {
    submission_id: &'a str,
    field_id: &'a str,
    type_id: &'a str,
    name: &'a str,
    content: &'a [u8],
}

#[cfg(test)]
mod tests {
    use super::*;
    use contest::Contest;

    #[test]
    fn test_submission_insert() {
        let tmp = tempdir::TempDir::new("tests").unwrap();
        let db = tmp.path().join("db.sqlite");
        let pp = tmp.path().join("test-problem");
        std::fs::create_dir(&pp);
        let contest = Contest {
            database_url: db.to_owned(),
        };
        contest.init_db();
        contest.add_user("user", "x", "x");
        contest.add_problem("problem", &pp);
        let mut files = Vec::new();
        files.push(FileInput {
            field_id: "field1".to_owned(),
            type_id: "text/plain".to_owned(),
            name: "solution.cpp".to_owned(),
            content_base64: "dGVzdHRlc3R0ZXN0cHJvdmE=".to_owned(),
        });
        files.push(FileInput {
            field_id: "field2".to_owned(),
            type_id: "text/plain".to_owned(),
            name: "solution.cpp".to_owned(),
            content_base64: "dGVzdHRlc3R0ZXN0cHJvdmE=".to_owned(),
        });
        files.push(FileInput {
            field_id: "field3".to_owned(),
            type_id: "text/plain".to_owned(),
            name: "solution.cpp".to_owned(),
            content_base64: "dGVzdHRlc3R0ZXN0cHJvdmE=".to_owned(),
        });
        let sub = insert(&contest.connect_db().unwrap(), "user", "problem", files).unwrap();
        assert_eq!(sub.problem_name, "problem");
        assert_eq!(sub.user_id, "user");
        // assert_eq!(sub.files.len(), 3);
        // assert_eq!(sub.files[0].content, b"testtesttestprova");
    }
}
