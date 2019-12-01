extern crate juniper;
extern crate serde_json;

use super::*;
use api::ApiContext;

pub fn generate_schema() {
    let context = ApiContext::default();
    let (schema, _errors) = juniper::introspect(
        &context.root_node(),
        &(),
        juniper::IntrospectionFormat::All,
    )
    .unwrap(); // TODO: GraphQLError doesn't yet implement Error trait... there is a PR open
    println!("{}", serde_json::to_string_pretty(&schema).unwrap());
}
