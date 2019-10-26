use super::*;

use schema::users;

#[derive(Insertable)]
#[table_name = "users"]
pub struct UserInput<'a> {
    id: &'a str,
    display_name: &'a str,
    token: &'a str,
}

#[derive(Queryable)]
pub struct User {
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

#[juniper::object(Context = Context)]
impl User {
    /// Id of the user
    fn id(&self) -> UserId {
        UserId(self.id.clone())
    }

    /// Display name of the user, i.e. the full name
    fn display_name(&self) -> &String {
        &self.display_name
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
