use super::*;

use schema::{submission_files, submissions};
use turingarena::submission::*;
use diesel::QueryResult;

/// File of a submission. (submission_id, field_id) is the primary key
#[derive(Queryable)]
#[allow(dead_code)]
pub struct SubmissionFile {
    /// id of the submmission
    submission_id: String,

    /// id of the field in the sumbission form
    field_id: String,

    /// type of the file (e.g MIME text/plain)
    type_id: String,

    /// name of the file, as uploaded by the user (ex. solution.cpp)
    name: String,

    /// content of the file as bytes
    content: Vec<u8>,
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
pub struct Submission {
    /// id of the submission, that is a random generated UUID
    pub id: String,

    /// id of user who made submission
    user_id: String,

    /// name of problem wich the submission refers to
    problem_name: String,

    /// time in wich the submission was created, saved as a RFC3339 date
    created_at: String,

    /// files submitted in this submission
    files: Vec<SubmissionFile>,
}

impl Submission {
    /// converts this submission to a TuringArena submission
    pub fn to_mem_submission(&self) -> mem::Submission {
        let mut field_values = Vec::new();
        for file in &self.files {
            field_values.push(FieldValue {
                field: form::FieldId(file.field_id.clone()),
                file: mem::File {
                    name: mem::FileName(file.name.clone()),
                    content: file.content.clone(),
                },
            })
        }
        mem::Submission { field_values }
    }
}

#[juniper::object]
impl Submission {
    /// UUID of the submission
    fn id(&self) -> &String {
        &self.id
    }

    /// id of the user who made the submission
    fn user_id(&self) -> &String {
        &self.user_id
    }

    /// name of the problem wich the submission refers to
    fn problem_name(&self) -> &String {
        &self.problem_name
    }

    /// time at wich the submission was created
    fn created_at(&self) -> &String {
        &self.created_at
    }

    /// list of files of this submission
    fn files(&self) -> &Vec<SubmissionFile> {
        &self.files
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

#[derive(Queryable)]
struct SubmissionTable {
    id: String,
    user_id: String,
    problem_name: String,
    created_at: String,
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

/// Insert a new submission into the database, returning a submission object
pub fn insert(
    conn: &SqliteConnection,
    user_id: &str,
    problem_name: &str,
    files: Vec<FileInput>,
) -> Result<Submission, Box<dyn std::error::Error>> {
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
        .execute(conn)?;
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
            .execute(conn)?;
    }
    Ok(query(conn, &id)?)
}

/// Gets the files of a submission
fn submission_files(conn: &SqliteConnection, submission_id: &str) -> QueryResult<Vec<SubmissionFile>> {
    submission_files::table
        .filter(submission_files::dsl::submission_id.eq(submission_id))
        .load::<SubmissionFile>(conn)
}

/// Gets the submission with the specified id from the database
pub fn query(conn: &SqliteConnection, id: &str) -> QueryResult<Submission> {
    let submission = submissions::table
        .filter(submissions::dsl::id.eq(id))
        .first::<SubmissionTable>(conn)?;
    Ok(Submission {
        id: submission.id,
        user_id: submission.user_id,
        problem_name: submission.problem_name,
        created_at: submission.created_at,
        files: submission_files(conn, id)?,
    })
}

/// Gets all the submissions of the specified user 
pub fn of_user(conn: &SqliteConnection, user_id: &str) -> QueryResult<Vec<Submission>> {
    Ok(submissions::table
        .filter(submissions::dsl::user_id.eq(user_id))
        .load::<SubmissionTable>(conn)?
        .into_iter()
        .map(|s| Submission {
            id: s.id.clone(),
            user_id: s.user_id,
            problem_name: s.problem_name,
            created_at: s.created_at,
            files: submission_files(conn, &s.id).unwrap(),
        }).collect())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contest::Contest;

    #[test]
    fn test_submission_insert() {
        let tmp = tempdir::TempDir::new("tests").unwrap();
        let db = tmp.path().join("db.sqlite");
        let pp = tmp.path().join("test-problem");
        std::fs::create_dir(&pp);
        let contest = Contest {
            database_url: db.to_owned(),
            problems_dir: tmp.path().to_owned(),
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
        assert_eq!(sub.files.len(), 3);
        assert_eq!(sub.files[0].content, b"testtesttestprova");
    }
}
