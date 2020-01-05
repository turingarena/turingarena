use diesel::{ExpressionMethods, QueryDsl, RunQueryDsl};
use juniper::FieldResult;

use root::ApiContext;

use juniper_ext::*;
use schema::{submission_files, submissions};
use submission::FieldValue;

use crate::api::contest_evaluation::Evaluation;
use crate::api::user::UserId;
use crate::file::FileContent;

use super::*;
use crate::api::contest_problem::Problem;
use crate::data::file::FileContentInput;

/// Wraps a String that identifies a submission
#[derive(GraphQLNewtype)]
pub struct SubmissionId(pub String);

/// File of a submission. (submission_id, field_id) is the primary key
#[derive(Queryable)]
#[allow(dead_code)]
struct SubmissionFile {
    submission_id: String,
    field_id: String,
    type_id: String,
    name: String,
    content: Vec<u8>,
}

impl SubmissionFile {
    pub fn into_field_value(self) -> FieldValue {
        FieldValue {
            field: submission::FieldId(self.field_id),
            file: submission::File {
                name: submission::FileName(self.name),
                content: self.content,
            },
        }
    }
}

#[juniper::object]
impl SubmissionFile {
    /// ID the field
    fn field_id(&self) -> &String {
        &self.field_id
    }

    /// ID of the type of the file for the field
    fn type_id(&self) -> &String {
        &self.type_id
    }

    /// File name
    fn name(&self) -> &String {
        &self.name
    }

    /// File content
    fn content(&self) -> FileContent {
        FileContent(self.content.clone())
    }
}

/// A submission in the database
#[derive(Queryable, Clone)]
struct SubmissionData {
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
    data: SubmissionData,
}

impl Submission<'_> {
    /// Name of the problem wich the submission refers to
    pub fn problem_name(&self) -> &String {
        &self.data.problem_name
    }

    pub fn field_values(&self) -> FieldResult<Vec<FieldValue>> {
        Ok(submission_files::table
            .filter(submission_files::dsl::submission_id.eq(&self.data.id))
            .load::<SubmissionFile>(&self.context.database)?
            .into_iter()
            .map(|f| f.into_field_value())
            .collect())
    }

    /// Gets the submission with the specified id from the database
    pub fn by_id<'a>(context: &'a ApiContext, submission_id: &str) -> FieldResult<Submission<'a>> {
        let data = submissions::table
            .filter(submissions::dsl::id.eq(submission_id))
            .first::<SubmissionData>(&context.database)?;
        Ok(Submission { context, data })
    }

    pub fn list<'a>(context: &'a ApiContext) -> FieldResult<Vec<Submission<'a>>> {
        Ok(submissions::table
            .load::<SubmissionData>(&context.database)?
            .into_iter()
            .map(|data| Submission { context, data })
            .collect())
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
        let submission = SubmissionInsertable {
            id: &id,
            user_id,
            problem_name,
            created_at: &created_at,
        };
        diesel::insert_into(submissions::table)
            .values(submission)
            .execute(&context.database)?;
        for file in files {
            let submission_file = SubmissionFileInsertable {
                submission_id: &id,
                field_id: &file.field_id,
                type_id: &file.type_id,
                name: &file.name,
                content: &file.content.decode()?,
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

    pub fn problem(&self) -> FieldResult<Problem> {
        Ok(Problem::by_name(&self.context, self.problem_name())?)
    }

    /// Time at wich the submission was created
    pub fn created_at(&self) -> &String {
        &self.data.created_at
    }

    /// List of files of this submission
    fn files(&self) -> FieldResult<Vec<SubmissionFile>> {
        Ok(submission_files::table
            .filter(submission_files::dsl::submission_id.eq(&self.data.id))
            .load::<SubmissionFile>(&self.context.database)?)
    }

    pub fn evaluation(&self) -> FieldResult<Evaluation> {
        Evaluation::of_submission(self.context, &self.data.id)
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

    /// Content of the file
    content: FileContentInput,
}

#[derive(Insertable)]
#[table_name = "submissions"]
struct SubmissionInsertable<'a> {
    id: &'a str,
    user_id: &'a str,
    problem_name: &'a str,
    created_at: &'a str,
}

#[derive(Insertable)]
#[table_name = "submission_files"]
struct SubmissionFileInsertable<'a> {
    submission_id: &'a str,
    field_id: &'a str,
    type_id: &'a str,
    name: &'a str,
    content: &'a [u8],
}

// TODO: fails to compile
//#[cfg(test)]
//mod tests {
//    use contest::Contest;
//
//    use super::*;
//
//    #[test]
//    fn test_submission_insert() {
//        let tmp = tempdir::TempDir::new("tests").unwrap();
//        let db = tmp.path().join("db.sqlite");
//        let pp = tmp.path().join("test-problem");
//        std::fs::create_dir(&pp);
//        let contest = Contest {
//            database_url: db.to_owned(),
//        };
//        contest.init_db();
//        contest.add_user("user", "x", "x");
//        contest.add_problem("problem", &pp);
//        let mut files = Vec::new();
//        files.push(FileInput {
//            field_id: "field1".to_owned(),
//            type_id: "text/plain".to_owned(),
//            name: "solution.cpp".to_owned(),
//            content_base64: "dGVzdHRlc3R0ZXN0cHJvdmE=".to_owned(),
//        });
//        files.push(FileInput {
//            field_id: "field2".to_owned(),
//            type_id: "text/plain".to_owned(),
//            name: "solution.cpp".to_owned(),
//            content_base64: "dGVzdHRlc3R0ZXN0cHJvdmE=".to_owned(),
//        });
//        files.push(FileInput {
//            field_id: "field3".to_owned(),
//            type_id: "text/plain".to_owned(),
//            name: "solution.cpp".to_owned(),
//            content_base64: "dGVzdHRlc3R0ZXN0cHJvdmE=".to_owned(),
//        });
//        let sub = insert(&contest.connect_db().unwrap(), "user", "problem", files).unwrap();
//        assert_eq!(sub.problem_name, "problem");
//        assert_eq!(sub.user_id, "user");
//        // assert_eq!(sub.files.len(), 3);
//        // assert_eq!(sub.files[0].content, b"testtesttestprova");
//    }
//}
