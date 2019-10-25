use graphql_client::{GraphQLQuery, Response};

use crate::client::request;
use crate::token;
use crate::user;

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "__generated__/graphql-schema.json",
    query_path = "graphql/auth.graphql",
    response_derives = "Debug"
)]
struct AuthQuery;

fn auth_request(user: String, password: String) -> Response<auth_query::ResponseData> {
    let variables = auth_query::Variables { user, password };
    let request_body = AuthQuery::build_query(variables);
    request(&request_body)
}

/// login to TuringArena server
pub fn login(username: String) {
    println!("Logging in as {}", username);
    let password = rpassword::read_password_from_tty(Some("Password: ")).unwrap();
    let response = auth_request(username, password);

    if let Some(errors) = response.errors {
        for error in errors {
            eprintln!("Error authenticating: {}", error.message);
        }
        panic!("Error submitting query");
    }

    if let Some(data) = response.data {
        token::store(data.auth.token);
        println!("Welcome, {}", user::current().display_name);
    }
}

/// Logout from the TuringArena server
pub fn logout() {
    token::delete();
}
