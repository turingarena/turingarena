use super::*;

use api::ApiContext;
use diesel::{ExpressionMethods, QueryDsl, QueryResult, RunQueryDsl, SqliteConnection};
use juniper_ext::*;
use schema::users;

#[derive(Debug, juniper::GraphQLInputObject)]
pub struct UserInput {
    /// Id of the user
    pub id: String,
    /// Display name of the user
    pub display_name: String,
    /// Login token of the user
    pub token: String,
}

#[derive(Insertable)]
#[table_name = "users"]
pub struct UserInsertable<'a> {
    id: &'a str,
    display_name: &'a str,
    token: &'a str,
}

#[derive(Queryable)]
pub struct User {
    id: String,
    display_name: String,
    #[allow(dead_code)]
    token: String,
}

/// Wraps a String that identifies a user
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize, GraphQLNewtype)]
pub struct UserId(pub String);

#[graphql]
impl User {
    /// Id of the user
    pub fn id(&self) -> UserId {
        UserId(self.id.clone())
    }

    /// Display name of the user, i.e. the full name
    pub fn display_name(&self) -> &String {
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

/// List all users
pub fn list(conn: &SqliteConnection) -> QueryResult<Vec<User>> {
    Ok(users::table.load(conn)?)
}

/// Insert a new user in the db
pub fn insert<T: IntoIterator<Item = UserInput>>(conn: &SqliteConnection, inputs: T) -> QueryResult<()> {
    // FIXME: replace_into not supported by PostgreSQL
    for input in inputs.into_iter() {
        diesel::replace_into(users::table)
            .values(UserInsertable {
                id: &input.id,
                display_name: &input.display_name,
                token: &input.token,
            })
            .execute(conn)?;
    }
    Ok(())
}

/// Delete a user from the db
pub fn delete<T: IntoIterator<Item = String>>(conn: &SqliteConnection, ids: T) -> QueryResult<()> {
    diesel::delete(users::table).filter(users::dsl::id.eq_any(ids)).execute(conn)?;
    Ok(())
}
