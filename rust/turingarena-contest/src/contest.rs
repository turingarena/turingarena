use juniper::{FieldResult, FieldError};

use crate::*;
use schema::{users, problems};

pub struct Contest;

/// a user authorization token 
#[derive(juniper::GraphQLObject)]
pub struct UserToken {
    token: Option<String>
}

#[juniper::object(Context = Context)]
impl Contest {
    fn auth(context: &Context, user: String, password: String) -> FieldResult<UserToken> {
        let connection = context.connect_db()?;
        let user = users::table.find(user).first(&connection)?;
        Ok(UserToken {
            token: auth::auth(&user, &password)
        })
    }

    fn user(context: &Context, id: Option<String>) -> FieldResult<user::User> {
        let connection = context.connect_db()?;
        let id = if let Some(id) = &id { 
            id 
        } else if let Some(ctx) = &context.jwt_data {
            &ctx.user 
        } else {
            return Err(FieldError::from("invalid authorization token"));
        };
        
        Ok(users::table.find(id).first(&connection)?)
    }

    fn problems(context: &Context) -> FieldResult<Vec<problem::Problem>> {
        let connection = context.connect_db()?;
        return Ok(problems::table.load::<problem::Problem>(&connection)?);
    }
}
