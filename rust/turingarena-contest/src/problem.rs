use super::*;

use schema::problems;

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
}
