use super::*;

use juniper::FieldResult;
use problem::Problem;
use schema::users;

#[derive(Insertable)]
#[table_name = "users"]
pub struct UserInput {
    pub id: String,
    pub display_name: String,
    pub password_bcrypt: String,
}

#[derive(Queryable)]
pub struct User {
    pub id: String,
    pub display_name: String,
    pub password_bcrypt: String,
}

/// Wraps a String that identifies a user
#[derive(juniper::GraphQLScalarValue)]
pub struct UserId(pub String);

/// A user
#[juniper::object(Context = Context)]
impl User {
    /// ID of this user. Should never be shown to any (non-admin) user.
    fn id(&self) -> UserId {
        return UserId(self.id.clone());
    }

    /// Name of this user to be shown to them or other users.
    fn display_name(&self) -> String {
        return self.display_name.clone();
    }

    /// List of problems that the user can see
    fn problems(&self, ctx: &Context) -> FieldResult<Option<Vec<Problem>>> {
        // TODO: return only the problems that only the user can access
        let problems = ctx
            .contest
            .get_problems()?
            .into_iter()
            .map(|p| Problem {
                data: p,
                user_id: Some(UserId(self.id.clone())),
            })
            .collect();
        Ok(Some(problems))
    }
}
