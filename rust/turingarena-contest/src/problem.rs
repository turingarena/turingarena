use super::*;
use juniper::FieldResult;

const DDL: &str = "
DROP TABLE IF EXISTS problems;
CREATE TABLE problems (
    name TEXT PRIMARY KEY
);
";

table! {
    problems (name) {
        name -> Text,
    }
}

#[derive(Insertable, juniper::GraphQLInputObject)]
#[table_name = "problems"]
pub struct ProblemInput {
    pub name: String,
}

#[derive(Queryable)]
pub struct Problem {
    pub name: String,
}

/// A problem
#[juniper::object(Context = Context)]
impl Problem {
    /// Name of this problem. Unique in the current contest.
    fn name(context: &Context) -> String {
        return self.name.clone();
    }
}

pub struct ProblemRepository;

impl ProblemRepository {
    pub fn init(context: &Context) -> FieldResult<MutationOk> {
        let connection = context.connect_db()?;
        connection.execute(DDL)?;
        Ok(MutationOk)
    }
}
