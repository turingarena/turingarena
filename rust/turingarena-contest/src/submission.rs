use super::*;
use juniper::FieldResult;

const DDL: &str = "
DROP TABLE IF EXISTS submissions;
DROP TABLE IF EXISTS submission_files;

CREATE TABLE submissions (
    id TEXT PRIMARY KEY,

    user_id TEXT NOT NULL,
    problem_name TEXT NOT NULL,

    created_at TEXT NOT NULL,
);

CREATE TABLE submission_files (
    submission_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    type_id TEXT NOT NULL,
    name TEXT NOT NULL,
    content_base64 TEXT NOT NULL,

    PRIMARY KEY (submission_id, field_id)
);
";

table! {
    submissions (id) {
        id -> Text,
        user_id -> Text,
        problem_name -> Text,
        created_at -> Text,
    }
}

table! {
    submission_files (submission_id, field_id) {
        submission_id -> Text,
        field_id -> Text,
        type_id -> Text,
        name -> Text,
        content_base64 -> Text,
    }
}

#[derive(Insertable, juniper::GraphQLInputObject)]
#[table_name = "submission_files"]
pub struct SubmissionFileInput {
    field_id: String,
    type_id: String,
    name: String,
    content_base64: String,
}

pub struct SubmissionRepository;

#[juniper::object(Context = Context)]
impl SubmissionRepository {
    fn init(context: &Context) -> FieldResult<MutationOk> {
        let connection = context.connect_db()?;
        connection.execute(DDL)?;
        Ok(MutationOk)
    }
}
