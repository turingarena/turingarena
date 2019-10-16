use super::*;

use schema::{submission_files};

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
}
