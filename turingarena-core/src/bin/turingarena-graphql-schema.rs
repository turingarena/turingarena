use turingarena_core::contest::graphql_schema::generate_schema;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    generate_schema()
}
