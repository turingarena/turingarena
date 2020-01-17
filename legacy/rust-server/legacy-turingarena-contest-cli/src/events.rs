use crate::client;
use graphql_client::{GraphQLQuery, Response};

#[derive(GraphQLQuery)]
#[graphql(
    schema_path = "__generated__/graphql-schema.json",
    query_path = "graphql/events.graphql",
    response_derives = "Debug"
)]
struct EventsQuery;

pub fn events(submission_id: String) {
    let body = EventsQuery::build_query(events_query::Variables { submission_id });
    let response: Response<events_query::ResponseData> = client::authenticated_request(&body);

    if let Some(errors) = response.errors {
        for error in errors {
            eprintln!("Error getting user informations: {}", error.message);
        }
        panic!("Error submitting query");
    }

    for event in response.data.unwrap().events {
        println!("{}", event.event_json);
    }
}
