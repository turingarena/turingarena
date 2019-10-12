#![feature(decl_macro, proc_macro_hygiene)]

extern crate turingarena_contest_webcontent;

use rocket::{
    http::{ContentType, Status},
    response::{self, content},
    State,
};
use std::ffi::OsStr;
use std::io::Cursor;
use std::path::PathBuf;
use turingarena_contest::*;
use turingarena_contest_webcontent::WebContent;

#[rocket::get("/graphiql")]
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

#[rocket::get("/")]
fn index<'r>() -> rocket::response::Result<'r> {
    dist(Some(PathBuf::from("index.html")))
}

#[rocket::get("/<file_option..>")]
fn dist<'r>(file_option: Option<PathBuf>) -> rocket::response::Result<'r> {
    let file = file_option.unwrap_or(PathBuf::new());
    let filename = file.display().to_string();
    let content = WebContent::get(&filename)
        .or(WebContent::get("index.html"))
        .unwrap();
    let ext = file
        .as_path()
        .extension()
        .and_then(OsStr::to_str)
        .unwrap_or("html");
    let content_type = ContentType::from_extension(ext)
        .ok_or(Status::new(400, "Could not get file content type"))?;
    response::Response::build()
        .header(content_type)
        .sized_body(Cursor::new(content))
        .ok()
}

fn main() {
    rocket::ignite()
        .manage(Schema::new(contest::Contest, contest::Contest))
        .manage(Context {})
        .mount(
            "/",
            rocket::routes![graphiql, get_graphql_handler, post_graphql_handler, index, dist],
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
