use super::*;

use juniper::FieldResult;
use problem::Problem;
use schema::users;
use turingarena::problem::ProblemName;

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

    /// A problem that the user can see
    fn problem(&self, ctx: &Context, name: ProblemName) -> FieldResult<Problem> {
        // TODO: check permissions
        let data = problem::by_name(&ctx.contest.connect_db()?, name)?;
        Ok(Problem {
            data,
            user_id: Some(UserId(self.id.clone())),
        })
    }

    /// List of problems that the user can see
    fn problems(&self, ctx: &Context) -> FieldResult<Option<Vec<Problem>>> {
        // TODO: return only the problems that only the user can access
        let problems = problem::all(&ctx.contest.connect_db()?)?
            .into_iter()
            .map(|p| Problem {
                data: p,
                user_id: Some(UserId(self.id.clone())),
            })
            .collect();
        Ok(Some(problems))
    }

    /// Title of the contest, as shown to the user
    fn contest_title(&self, ctx: &Context) -> FieldResult<String> {
        Ok(config::current_config(&ctx.contest.connect_db()?)?.contest_title)
    }

    /// Start time of the user participation, as RFC3339 date
    fn start_time(&self, ctx: &Context) -> FieldResult<String> {
        Ok(config::current_config(&ctx.contest.connect_db()?)?.start_time)
    }

    /// End time of the user participation, as RFC3339 date
    fn end_time(&self, ctx: &Context) -> FieldResult<String> {
        Ok(config::current_config(&ctx.contest.connect_db()?)?.end_time)
    }
}

/// Find a user from his token
pub fn by_token(conn: &SqliteConnection, token: &str) -> QueryResult<User> {
    users::table.filter(users::dsl::token.eq(token)).first(conn)
}

/// Find a user from his ID
pub fn by_id(conn: &SqliteConnection, user_id: UserId) -> QueryResult<User> {
    users::table.find(user_id.0).first(conn)
}

/// Insert a new user in the db
pub fn insert(
    conn: &SqliteConnection,
    user_id: UserId,
    display_name: &str,
    token: &str,
) -> QueryResult<()> {
    let user = UserInput {
        id: &user_id.0,
        display_name,
        token,
    };
    diesel::insert_into(users::table)
        .values(user)
        .execute(conn)?;
    Ok(())
}

/// Delete a user from the db
pub fn delete(conn: &SqliteConnection, user_id: UserId) -> QueryResult<()> {
    diesel::delete(users::table.find(user_id.0)).execute(conn)?;
    Ok(())
}
