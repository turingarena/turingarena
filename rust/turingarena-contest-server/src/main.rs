#![feature(decl_macro, proc_macro_hygiene)]

#[macro_use]
extern crate diesel;
extern crate juniper;
extern crate juniper_rocket;
extern crate rocket;

use diesel::prelude::*;
use juniper::FieldResult;

struct Context {}
impl juniper::Context for Context {}

impl Context {
    fn connect_db(&self) -> ConnectionResult<SqliteConnection> {
        SqliteConnection::establish("./test.sqlite")
    }
}

table! {
    tasks (name) {
        name -> Text,
    }
}

#[derive(Insertable, juniper::GraphQLInputObject)]
#[table_name = "tasks"]
struct TaskInput {
    pub name: String,
}

#[derive(Queryable)]
struct Task {
    pub name: String,
}

/// A task
#[juniper::object(Context = Context)]
impl Task {
    /// Name of this task. Unique in the current contest.
    fn name(&self) -> String {
        return self.name.clone();
    }
}

struct Contest;

#[juniper::object(Context = Context)]
impl Contest {
    fn tasks(context: &Context) -> FieldResult<Vec<Task>> {
        let connection = context.connect_db()?;
        return Ok(tasks::table.load::<Task>(&connection)?);
    }

    fn set_tasks(context: &Context, tasks: Vec<TaskInput>) -> FieldResult<Vec<Task>> {
        let connection = context.connect_db()?;
        connection.execute(
            "
            DROP TABLE IF EXISTS tasks;
            CREATE TABLE tasks (
                name TEXT PRIMARY KEY
            );
            ",
        )?;
        diesel::insert_into(tasks::table)
            .values(tasks)
            .execute(&connection)?;
        return Ok(tasks::table.load::<Task>(&connection)?);
    }
}

type Schema = juniper::RootNode<'static, Contest, Contest>;

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
        .manage(Schema::new(Contest, Contest))
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
