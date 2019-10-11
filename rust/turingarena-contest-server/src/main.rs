#![feature(decl_macro, proc_macro_hygiene)]

#[macro_use]
extern crate diesel;
extern crate juniper;
extern crate juniper_rocket;
extern crate rand;
extern crate rocket;

use diesel::prelude::*;

mod contest_config;
mod submission;

pub struct Context {}
impl juniper::Context for Context {}

impl Context {
    fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        SqliteConnection::establish("./test.sqlite")
    }
}

struct MutationOk;

#[juniper::object]
impl MutationOk {
    fn ok() -> bool {
        true
    }
}

type Schema = juniper::RootNode<'static, contest_config::Contest, contest_config::Contest>;

use rocket::{response::content, State};

#[rocket::get("/")]
fn graphiql() -> content::Html<String> {
    juniper_rocket::graphiql_source("/graphql")
}

#[rocket::get("/graphql?<request>")]
fn get_graphql_handler(
    context: State<Context>,
    request: juniper_rocket::GraphQLRequest,
    schema: State<Schema>,
) -> juniper_rocket::GraphQLResponse {
    request.execute(&schema, &context)
}

#[rocket::post("/graphql", data = "<request>")]
fn post_graphql_handler(
    context: State<Context>,
    request: juniper_rocket::GraphQLRequest,
    schema: State<Schema>,
) -> juniper_rocket::GraphQLResponse {
    request.execute(&schema, &context)
}

fn main() {
    rocket::ignite()
        .manage(Schema::new(
            contest_config::Contest,
            contest_config::Contest,
        ))
        .manage(Context {})
        .mount(
            "/",
            rocket::routes![graphiql, get_graphql_handler, post_graphql_handler],
        )
        .launch();
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
