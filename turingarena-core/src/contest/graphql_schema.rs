use crate::contest::api::ApiConfig;

pub fn generate_schema() -> Result<(), Box<dyn std::error::Error>> {
    let config = ApiConfig::default();
    let context = config.create_context(None);
    let (schema, _errors) =
        juniper::introspect(&context.root_node(), &(), juniper::IntrospectionFormat::All).unwrap(); // TODO: GraphQLError doesn't yet implement Error trait... there is a PR open
    println!("{}", serde_json::to_string_pretty(&schema)?);
    Ok(())
}
