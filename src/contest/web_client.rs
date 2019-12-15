use rust_embed::RustEmbed;

#[derive(RustEmbed)]
#[folder = "$OUT_DIR/web/dist/turingarena-contest"]
pub struct WebContent;
