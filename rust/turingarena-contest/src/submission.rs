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
    }
    Ok(query(conn, &submission_id)?)
}

/// Gets the submission with the specified id from the database
pub fn query(conn: &SqliteConnection, id: &str) -> Result<Submission, Box<dyn std::error::Error>> {
    let (id, user_id, problem_name, created_at) = submissions::table
        .filter(submissions::dsl::id.eq(id))
        .first::<(String, String, String, String)>(conn)?;
    let files = submission_files::table
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
        let sub = insert(&contest.connect_db().unwrap(), "user", "problem", files).unwrap();
        assert_eq!(sub.problem_name, "problem");
        assert_eq!(sub.user_id, "user");
        assert_eq!(sub.files.len(), 3);
        assert_eq!(sub.files[0].content_base64, "dGVzdHRlc3R0ZXN0cHJvdmEK");
    }
}
