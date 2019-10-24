use super::*;

extern crate turingarena;
extern crate turingarena_task_maker;

use schema::problems;
use turingarena::problem::driver::{ProblemDriver, ProblemPack};
use turingarena::problem::material::Material;
use turingarena::problem::ProblemName;

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
#[juniper::object]
impl ContestProblem {
    /// Name of this problem. Unique in the current contest.
    fn name(&self) -> ProblemName {
        ProblemName(self.name.clone())
    }

    /// Name of this problem. Unique in the current contest.
    fn material(&self) -> FieldResult<Material> {
        turingarena_task_maker::driver::IoiProblemDriver::gen_material(self.pack())
            .map_err(|e| FieldError::from(e))
    }
}

impl ContestProblem {
    /// return the problem pack object
    pub fn pack(&self) -> ProblemPack {
        ProblemPack(std::path::PathBuf::from(&self.path))
    }
}
