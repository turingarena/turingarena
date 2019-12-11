use diesel::{ExpressionMethods, QueryDsl, QueryResult, RunQueryDsl, SqliteConnection};
use juniper::FieldResult;

use api::ApiContext;
use juniper_ext::*;
use schema::users;

use super::*;

#[derive(Debug, juniper::GraphQLInputObject, Insertable)]
#[table_name = "users"]
pub struct UserInput {
    /// Id of the user
    pub id: String,
    /// Display name of the user
    pub display_name: String,
    /// Login token of the user
    pub token: String,
}

#[derive(Debug, juniper::GraphQLInputObject, AsChangeset)]
#[table_name = "users"]
pub struct UserUpdateInput {
    pub id: String,
    pub display_name: Option<String>,
    pub token: Option<String>,
}

#[derive(Queryable)]
struct UserData {
    id: String,
    display_name: String,
    #[allow(dead_code)]
    token: String,
}

pub struct User<'a> {
    context: &'a ApiContext<'a>,
    data: UserData,
}

/// Wraps a String that identifies a user
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize, GraphQLNewtype)]
pub struct UserId(pub String);

impl<'a> User<'a> {
    /// Find a user from his token
    pub fn by_token(context: &'a ApiContext, token: &str) -> FieldResult<Self> {
        Ok(Self {
            context,
            data: users::table
                .filter(users::dsl::token.eq(token))
                .first(&context.database)?,
        })
    }

    /// Find a user from his ID
    pub fn by_id(context: &'a ApiContext, user_id: UserId) -> FieldResult<Self> {
        Ok(Self {
            context,
            data: users::table.find(user_id.0).first(&context.database)?,
        })
    }

    /// List all users
    pub fn list(context: &'a ApiContext) -> FieldResult<Vec<Self>> {
        Ok(users::table
            .load(&context.database)?
            .into_iter()
            .map(|data| Self { context, data })
            .collect())
    }

    /// Insert a new user in the db
    pub fn insert<T: IntoIterator<Item = UserInput>>(
        context: &ApiContext,
        inputs: T,
    ) -> QueryResult<()> {
        for input in inputs.into_iter() {
            diesel::insert_into(users::table)
                .values(input)
                .execute(&context.database)?;
        }
        Ok(())
    }

    pub fn update<T: IntoIterator<Item = UserUpdateInput>>(
        context: &ApiContext,
        inputs: T,
    ) -> QueryResult<()> {
        for input in inputs.into_iter() {
            diesel::update(users::table)
                .filter(users::dsl::id.eq(&input.id))
                .set(&input)
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
impl User<'_> {
    /// Id of the user
    pub fn id(&self) -> UserId {
        UserId(self.data.id.clone())
    }

    /// Display name of the user, i.e. the full name
    pub fn display_name(&self) -> &String {
        &self.data.display_name
    }
}
