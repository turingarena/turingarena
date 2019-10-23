use crate::*;
use rocket::request::{self, FromRequest, Request};
use rocket::{
    http::{ContentType, Status},
    response::{self, content},
    Outcome, State,
};
use std::ffi::OsStr;
use std::io::Cursor;
use std::path::PathBuf;
use turingarena_contest_webcontent::WebContent;

struct Authorization(Option<String>);

impl<'a, 'r> FromRequest<'a, 'r> for Authorization {
    type Error = String;

    fn from_request(request: &'a Request<'r>) -> request::Outcome<Self, Self::Error> {
        request::Outcome::Success(Authorization(
            match request.headers().get_one("Authorization") {
                Some(token) => Some(token.to_owned()),
                None => None,
            },
        ))
    }
}

#[rocket::get("/graphiql")]
fn graphiql() -> content::Html<String> {
    juniper_rocket::graphiql_source("/graphql")
}

#[rocket::post("/graphql", data = "<request>")]
fn post_graphql_handler(
    request: juniper_rocket::GraphQLRequest,
    schema: State<Schema>,
    auth: Authorization,
) -> juniper_rocket::GraphQLResponse {
    let skip_auth = std::env::var("SKIP_AUTH").unwrap_or(String::new()) == "1";
    let secret_str = std::env::var("SECRET").unwrap_or(String::new());
    if secret_str == "" && !skip_auth {
        return juniper_rocket::GraphQLResponse::error(juniper::FieldError::from(
            "Cannot authenticate users: set environment variable SECRET or SKIP_AUTH=1",
        ));
    }
    let secret = secret_str.as_bytes().to_owned();
    let jwt_data = auth.0.map(|token| match auth::validate(&token, &secret) {
        Ok(claims) => claims,
        Err(_) => panic!("Invalid token"),
    });
    let context = Context {
        skip_auth,
        jwt_data,
        secret,
    };
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

pub fn run_server(host: String, port: u16) {
    let config = rocket::Config::build(rocket::config::Environment::active().unwrap())
        .port(port)
        .address(host)
        .finalize()
        .unwrap();

    rocket::custom(config)
        .manage(Schema::new(
            contest::Contest::from_env(),
            contest::Contest::from_env(),
        ))
        .mount(
            "/",
            rocket::routes![graphiql, post_graphql_handler, index, dist],
        )
        .launch();
}
