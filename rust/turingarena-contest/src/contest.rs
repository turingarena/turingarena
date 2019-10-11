use super::{problem::*, submission::*, user::*, *};
use juniper::FieldResult;

pub struct Contest;

#[juniper::object(Context = Context)]
impl Contest {
    fn init(context: &Context) -> FieldResult<MutationOk> {
        // TODO: check admin credentials
        UserRepository::init(context)?;
        ProblemRepository::init(context)?;
        let connection = context.connect_db()?;
        return Ok(MutationOk);
    }

    fn user(context: &Context, id: String) -> FieldResult<Vec<User>> {
        // TODO: check user credentials
        let connection = context.connect_db()?;
        return Ok(users::table.find(id).load::<User>(&connection)?);
    }

    fn problems(context: &Context) -> FieldResult<Vec<Problem>> {
        let connection = context.connect_db()?;
        return Ok(problems::table.load::<Problem>(&connection)?);
    }
}
