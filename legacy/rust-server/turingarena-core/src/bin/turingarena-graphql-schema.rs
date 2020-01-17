use turingarena_core::api::graphql_schema::run_generate_schema;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    run_generate_schema()
}
