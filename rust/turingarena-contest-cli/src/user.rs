use crate::client;
use graphql_client::{GraphQLQuery, Response};

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "__generated__/graphql-schema.json",
    query_path = "graphql/user.graphql",
    response_derives = "Debug"
)]
struct UserQuery;

/// get the current user
pub fn current() -> user_query::UserQueryUser {
    let body = UserQuery::build_query(user_query::Variables {});
    let response: Response<user_query::ResponseData> = client::authenticated_request(&body);

    if let Some(errors) = response.errors {
        for error in errors {
            eprintln!("Error getting user informations: {}", error.message);
        }
        panic!("Error submitting query");
    }

    response.data.unwrap().user
}

/// print user informations
pub fn info() {
    let user = current();
    println!("Currently logged in as {} ({})", user.display_name, user.id);
}
