use juniper::FieldResult;

use crate::*;
use schema::{users, problems};

pub struct Contest;

#[juniper::object(Context = Context)]
impl Contest {
    fn user(context: &Context, id: String) -> FieldResult<user::User> {
        // TODO: check user credentials
        let connection = context.connect_db()?;
        return Ok(users::table.find(id).first(&connection)?);
    }

    fn problems(context: &Context) -> FieldResult<Vec<problem::Problem>> {
        let connection = context.connect_db()?;
        return Ok(problems::table.load::<problem::Problem>(&connection)?);
    }
}
