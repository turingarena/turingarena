use super::*;

use juniper::FieldResult;
use problem::Problem;
use schema::users;
use turingarena::problem::ProblemName;

#[derive(Insertable)]
#[table_name = "users"]
pub struct UserDataInput<'a> {
    id: &'a str,
    display_name: &'a str,
    token: &'a str,
}

#[derive(Queryable)]
pub struct UserData {
    /// Id of the user
    pub id: String,

    /// Display name of the user
    display_name: String,

    /// Login token of the user
    #[allow(dead_code)]
    token: String,
}

/// Wraps a String that identifies a user
#[derive(Clone, juniper::GraphQLScalarValue)]
pub struct UserId(pub String);

/// A User structure
pub struct User {
    /// DB data of the user
    pub data: Option<UserData>,
}

impl User {
    /// Id of this user (if any)
    pub fn user_id(&self) -> Option<UserId> {
        self.data.as_ref().map(|u| UserId(u.id.clone()))
    }
}

/// A user
#[juniper::object(Context = Context)]
impl User {
    /// ID of this user. Should never be shown to any (non-admin) user.
    fn id(&self) -> Option<UserId> {
        self.user_id()
    }

    /// Name of this user to be shown to them or other users.
    fn display_name(&self) -> Option<String> {
        self.data.as_ref().map(|u| u.display_name.clone())
    }

    /// A problem that the user can see
    fn problem(&self, ctx: &Context, name: ProblemName) -> FieldResult<Problem> {
        // TODO: check permissions
        let data = problem::by_name(&ctx.connect_db()?, name)?;
        Ok(Problem {
            data,
            user_id: self.user_id(),
        })
    }

    /// List of problems that the user can see
    fn problems(&self, ctx: &Context) -> FieldResult<Option<Vec<Problem>>> {
        // TODO: return only the problems that only the user can access
        let problems = problem::all(&ctx.connect_db()?)?
            .into_iter()
            .map(|p| Problem {
                data: p,
                user_id: self.user_id(),
            })
            .collect();
        Ok(Some(problems))
    }

    /// Title of the contest, as shown to the user
    fn contest_title(&self, ctx: &Context) -> FieldResult<String> {
        Ok(config::current_config(&ctx.connect_db()?)?.contest_title)
    }

    /// Start time of the user participation, as RFC3339 date
    fn start_time(&self, ctx: &Context) -> FieldResult<String> {
        Ok(config::current_config(&ctx.connect_db()?)?.start_time)
    }

    /// End time of the user participation, as RFC3339 date
    fn end_time(&self, ctx: &Context) -> FieldResult<String> {
        Ok(config::current_config(&ctx.connect_db()?)?.end_time)
    }
}

/// Find a user from his token
pub fn by_token(conn: &SqliteConnection, token: &str) -> QueryResult<UserData> {
    users::table.filter(users::dsl::token.eq(token)).first(conn)
}

/// Find a user from his ID
pub fn by_id(conn: &SqliteConnection, user_id: UserId) -> QueryResult<UserData> {
    users::table.find(user_id.0).first(conn)
}

/// Insert a new user in the db
pub fn insert(
    conn: &SqliteConnection,
    user_id: UserId,
    display_name: &str,
    token: &str,
) -> QueryResult<()> {
    let user = UserDataInput {
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
