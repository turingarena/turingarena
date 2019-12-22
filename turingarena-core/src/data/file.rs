//! Data types to represent the content of files

use super::*;
use diesel::backend::Backend;
use diesel::deserialize::FromSql;

use diesel::serialize::{Output, ToSql};
use diesel::sql_types::Binary;

use serde::{Deserialize, Serialize};
use std::error::Error;
use std::io::Write;

/// Wraps the content of a file, as array of bytes.
#[derive(Serialize, Deserialize, Clone, Debug, FromSqlRow)]
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

impl<DB: Backend> FromSql<Binary, DB> for FileContent
where
    Vec<u8>: FromSql<Binary, DB>,
{
    fn from_sql(bytes: Option<&DB::RawValue>) -> diesel::deserialize::Result<Self> {
        let data = <Vec<u8> as FromSql<_, DB>>::from_sql(bytes)?;
        Ok(FileContent(data))
    }
}

/// Wraps the content of a file, as array of bytes.
#[derive(Serialize, Deserialize, Clone, Debug, juniper::GraphQLInputObject, AsExpression)]
#[sql_type = "Binary"]
pub struct FileContentInput {
    base64: String,
}

impl FileContentInput {
    pub fn decode(&self) -> Result<Vec<u8>, impl Error> {
        base64::decode(&self.base64)
    }
}

impl<DB: Backend> ToSql<Binary, DB> for FileContentInput {
    fn to_sql<W: Write>(&self, out: &mut Output<W, DB>) -> diesel::serialize::Result {
        <Vec<u8> as ToSql<Binary, DB>>::to_sql(&self.decode()?, out)
    }
}
