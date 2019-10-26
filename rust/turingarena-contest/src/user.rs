use super::*;

use juniper::FieldResult;
use problem::Problem;
use schema::users;

#[derive(Insertable)]
#[table_name = "users"]
pub struct UserInput<'a> {
    pub id: &'a str,
    pub display_name: &'a str,
    pub token: &'a str,
}

#[derive(Queryable)]
pub struct User {
    pub id: String,
    pub display_name: String,
    pub token: String,
}

/// Wraps a String that identifies a user
#[derive(Clone, juniper::GraphQLScalarValue)]
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

/// Find a user from his token
pub fn by_token(conn: &SqliteConnection, token: &str) -> QueryResult<User> {
    users::table
        .filter(users::dsl::token.eq(token))
        .first(conn)
}

/// Find a user from his ID
pub fn by_id(conn: &SqliteConnection, user_id: UserId) -> QueryResult<User> {
    users::table
        .find(user_id.0)
        .first(conn)
}