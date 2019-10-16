use rust_embed::RustEmbed;

#[derive(RustEmbed)]
#[folder = "$CARGO_MANIFEST_DIR/../../web/dist/turingarena-contest/"]
pub struct WebContent;
