use super::*;

extern crate turingarena;

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

    /// Name of this problem. Unique in the current contest.
    fn material(context: &Context) -> turingarena::problem::material::Material {
        unimplemented!();
    }
}

pub struct ProblemRepository;

impl ProblemRepository {
}
