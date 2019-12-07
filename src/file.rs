//! Data types to represent the content of files

extern crate base64;
extern crate serde;

use super::*;
use juniper::FieldResult;
use serde::{Deserialize, Serialize};

/// Wraps the content of a file, as array of bytes.
#[derive(Serialize, Deserialize, Clone)]
pub struct FileContent(pub Vec<u8>);

// We cannot use `#[juniper::object]` because it does not support generic scalars,
// which are required by `#[derive(GraphQLObject)]` for all the fields.
juniper::graphql_object!(FileContent: () where Scalar = <S> |&self| {
    field base64() -> String {
        base64::encode(&self.0)
    }

    field text() -> Option<String> {
        String::from_utf8(self.0.clone()).ok()
    }
});

/// Wraps the content of a file, as array of bytes.
#[derive(Serialize, Deserialize, Clone, juniper::GraphQLInputObject)]
pub struct FileContentInput {
    base64: String,
}

impl FileContentInput {
    pub fn decode(&self) -> FieldResult<Vec<u8>> {
        Ok(base64::decode(&self.base64)?)
    }
}
