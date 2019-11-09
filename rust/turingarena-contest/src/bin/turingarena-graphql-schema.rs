use turingarena_contest::server::generate_schema;
use turingarena_contest::api::ApiContext;

fn main() {
    generate_schema(ApiContext::default()).unwrap();
}
