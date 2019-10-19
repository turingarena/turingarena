use super::*;

use schema::{submission_files, submissions};

/// File of a submission. (submission_id, field_id) is the primary key
#[derive(juniper::GraphQLObject)]
pub struct SubmissionFile {
    /// id of the submmission
    submission_id: String,

    /// id of the field in the sumbission form
    field_id: String,

    /// type of the file (e.g MIME text/plain)
    type_id: String,

    /// name of the file, as uploaded by the user (ex. solution.cpp)
    name: String,

    /// content of the file codified in the base64 format
    content_base64: String,
}

/// A submission in the database
#[derive(juniper::GraphQLObject)]
pub struct Submission {
    /// id of the submission, that is a random generated UUID
    id: String,

    /// id of user who made submission
    user_id: String,

    /// name of problem wich the submission refers to
    problem_name: String,

    /// time in wich the submission was created, saved as a RFC3339 date
    created_at: String,

    /// files submitted in this submission
    files: Vec<SubmissionFile>,
}

/// Input file for a submission file
#[derive(juniper::GraphQLInputObject)]
pub struct GraphQLFileInput {
    /// type of the file submitted
    type_id: String,

    /// name of the field that this file refears to
    field_id: String,

    /// filename as uploaded by the user
    name: String,

    /// content of the file codified in base64
    content_base64: String,
}

<<<<<<< HEAD
#[derive(Queryable, Insertable)]
#[table_name = "submissions"]
struct SubmissionTable {
    id: String,
    user_id: String,
    problem_name: String,
    created_at: String,
}

#[derive(Queryable, Insertable)]
#[table_name = "submission_files"]
struct SubmissionFileTable {
    submission_id: String,
    field_id: String,
    type_id: String,
    name: String,
    content: Vec<u8>,
}

/// Insert a new submission into the database, returning a submission object
pub fn insert(
        conn: &SqliteConnection, 
        user_id: String, 
        problem_name: String, 
        files: Vec<GraphQLFileInput>
    ) -> Result<Submission, Box<dyn std::error::Error>> {
    let id = uuid::Uuid::new_v4().to_string();
    let created_at = chrono::Local::now().to_rfc3339();
    let submission = SubmissionTable {
        id: id.clone(),
        user_id, 
        problem_name,
        created_at,
    };
    diesel::insert_into(submissions::table).values(submission).execute(conn)?;
    for file in files {
        let submission_file = SubmissionFileTable {
            submission_id: id.clone(),
            field_id: file.field_id,
            type_id: file.type_id,
            name: file.name,
            content: base64::decode(&file.content_base64)?,
        };
        diesel::insert_into(submission_files::table).values(submission_file).execute(conn)?;
=======
/// Insert a new submission into the database, returning a submission object
pub fn insert(
    conn: &SqliteConnection,
    user: &str,
    problem: &str,
    files: Vec<GraphQLFileInput>,
) -> Result<Submission, Box<dyn std::error::Error>> {
    let submission_id = uuid::Uuid::new_v4().to_string();
    diesel::insert_into(submissions::table)
        .values((
            submissions::dsl::id.eq(&submission_id),
            submissions::dsl::user_id.eq(user),
            submissions::dsl::problem_name.eq(problem),
            submissions::dsl::created_at.eq(chrono::Local::now().to_rfc3339()),
        ))
        .execute(conn)?;
    for file in files {
        diesel::insert_into(submission_files::table)
            .values((
                submission_files::dsl::submission_id.eq(&submission_id),
                submission_files::dsl::type_id.eq(file.type_id),
                submission_files::dsl::field_id.eq(file.field_id),
                submission_files::dsl::name.eq(file.name),
                submission_files::dsl::content.eq(base64::decode(&file.content_base64)?),
            ))
            .execute(conn)?;
>>>>>>> 2a017edb3b600ab404faeebb3becda009a2dea06
    }
    Ok(query(conn, id)?)
}

/// Gets the submission with the specified id from the database
pub fn query(conn: &SqliteConnection, id: String) -> Result<Submission, Box<dyn std::error::Error>> {
    let submission = submissions::table.filter(submissions::dsl::id.eq(id)).first::<SubmissionTable>(conn)?;
    let files = submission_files::table
<<<<<<< HEAD
        .load::<SubmissionFileTable>(conn)?
        .into_iter()
        .map(|submission_file| SubmissionFile {
            submission_id: submission_file.submission_id,
            field_id: submission_file.field_id, 
            type_id: submission_file.type_id, 
            name: submission_file.name, 
            content_base64: base64::encode(&submission_file.content),
        }).collect();
    Ok(Submission { 
        id: submission.id, 
        user_id: submission.user_id, 
        problem_name: submission.problem_name, 
        created_at: submission.created_at, 
        files 
=======
        .load::<(String, String, String, String, Vec<u8>)>(conn)?
        .iter()
        .map(
            |(submission_id, field_id, type_id, name, content)| SubmissionFile {
                submission_id: submission_id.to_owned(),
                field_id: field_id.to_owned(),
                type_id: type_id.to_owned(),
                name: name.to_owned(),
                content_base64: base64::encode(&content),
            },
        )
        .collect();
    Ok(Submission {
        id,
        user_id,
        problem_name,
        created_at,
        files,
>>>>>>> 2a017edb3b600ab404faeebb3becda009a2dea06
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::contest::Contest;

    #[test]
    fn test_submission_insert() {
        let db = tempdir::TempDir::new("tests").unwrap();
        let db = db.path().join("db.sqlite");
        let contest = Contest::with_database(db.to_str().unwrap());
        contest.init_db();
        contest.add_user("user", "x", "x");
        contest.add_problem("problem", "test-path");
        let mut files = Vec::new();
        files.push(GraphQLFileInput {
            field_id: "field1".to_owned(),
            type_id: "text/plain".to_owned(),
            name: "solution.cpp".to_owned(),
            content_base64: "dGVzdHRlc3R0ZXN0cHJvdmEK".to_owned(),
        });
        files.push(GraphQLFileInput {
            field_id: "field2".to_owned(),
            type_id: "text/plain".to_owned(),
            name: "solution.cpp".to_owned(),
            content_base64: "dGVzdHRlc3R0ZXN0cHJvdmEK".to_owned(),
        });
        files.push(GraphQLFileInput {
            field_id: "field3".to_owned(),
            type_id: "text/plain".to_owned(),
            name: "solution.cpp".to_owned(),
            content_base64: "dGVzdHRlc3R0ZXN0cHJvdmEK".to_owned(),
        });
        let sub = insert(&contest.connect_db().unwrap(), "user".to_owned(), "problem".to_owned(), files).unwrap();
        assert_eq!(sub.problem_name, "problem");
        assert_eq!(sub.user_id, "user");
        assert_eq!(sub.files.len(), 3);
        assert_eq!(sub.files[0].content_base64, "dGVzdHRlc3R0ZXN0cHJvdmEK");
    }
}
