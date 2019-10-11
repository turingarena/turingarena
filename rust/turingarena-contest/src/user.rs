use juniper::FieldResult;

use super::*;

const DDL: &str = "
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    display_name TEXT
);
";

table! {
    users (id) {
        id -> Text,
        display_name -> Text,
    }
}

#[derive(Insertable, juniper::GraphQLInputObject)]
#[table_name = "users"]
pub struct UserInput {
    pub id: Option<String>,
    pub display_name: Option<String>,
}

#[derive(Queryable)]
pub struct User {
    pub id: String,
    pub display_name: String,
}

/// A task
#[juniper::object(Context = Context)]
impl User {
    fn id(&self) -> String {
        return self.id.clone();
    }

    /// Name of this task. Unique in the current contest.
    fn display_name(&self) -> String {
        return self.display_name.clone();
    }
}

pub struct UserRepository;

impl UserRepository {
    pub fn init(context: &Context) -> FieldResult<MutationOk> {
        let connection = context.connect_db()?;
        connection.execute(DDL)?;
        Ok(MutationOk)
    }
}
