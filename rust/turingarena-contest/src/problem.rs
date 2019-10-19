use super::*;

extern crate turingarena;
extern crate turingarena_task_maker;

use schema::problems;
use turingarena::problem::{
    driver::{ProblemDriver, ProblemPack},
    material::Material,
    ProblemName,
};

use juniper::{FieldError, FieldResult};

#[derive(Insertable, juniper::GraphQLInputObject)]
#[table_name = "problems"]
pub struct ContestProblemInput {
    pub name: String,
    pub path: String,
}

#[derive(Queryable)]
pub struct ContestProblem {
    pub name: String,
    pub path: String,
}

/// A problem in a contest
#[juniper::object(Context = Context)]
impl ContestProblem {
    /// Name of this problem. Unique in the current contest.
    fn name(&self, context: &Context) -> ProblemName {
        return ProblemName(self.name.clone());
    }

    /// Name of this problem. Unique in the current contest.
    fn material(context: &Context) -> FieldResult<Material> {
        turingarena_task_maker::driver::IoiProblemDriver::gen_material(ProblemPack(
            std::path::PathBuf::from(self.path.clone()),
        ))
        .map_err(|e| FieldError::from(e))
    }
}
