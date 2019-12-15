use crate::contest::api::ApiConfig;

pub fn generate_schema() -> String {
    let config = ApiConfig::default();
    let context = config.create_context(None);
    let (schema, _errors) =
        juniper::introspect(&context.root_node(), &(), juniper::IntrospectionFormat::All).unwrap(); // TODO: GraphQLError doesn't yet implement Error trait... there is a PR open
    serde_json::to_string_pretty(&schema).unwrap()
}
