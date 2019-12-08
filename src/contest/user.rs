use super::*;

use api::ApiContext;
use diesel::{ExpressionMethods, QueryDsl, QueryResult, RunQueryDsl, SqliteConnection};
use juniper::FieldResult;
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

impl User {
    /// Find a user from his token
    pub fn by_token(context: &ApiContext, token: &str) -> FieldResult<User> {
        Ok(users::table
            .filter(users::dsl::token.eq(token))
            .first(&context.database)?)
    }

    /// Find a user from his ID
    pub fn by_id(context: &ApiContext, user_id: UserId) -> FieldResult<User> {
        Ok(users::table.find(user_id.0).first(&context.database)?)
    }

    /// List all users
    pub fn list(context: &ApiContext) -> FieldResult<Vec<User>> {
        Ok(users::table.load(&context.database)?)
    }

    /// Insert a new user in the db
    pub fn insert<T: IntoIterator<Item = UserInput>>(
        context: &ApiContext,
        inputs: T,
    ) -> QueryResult<()> {
        for input in inputs.into_iter() {
            // FIXME: replace_into not supported by PostgreSQL
            diesel::replace_into(users::table)
                .values(UserInsertable {
                    id: &input.id,
                    display_name: &input.display_name,
                    token: &input.token,
                })
                .execute(&context.database)?;
        }
        Ok(())
    }

    /// Delete a user from the db
    pub fn delete<T: IntoIterator<Item = String>>(context: &ApiContext, ids: T) -> QueryResult<()> {
        diesel::delete(users::table)
            .filter(users::dsl::id.eq_any(ids))
            .execute(&context.database)?;
        Ok(())
    }
}

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
