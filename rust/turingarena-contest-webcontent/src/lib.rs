use rust_embed::RustEmbed;

#[derive(RustEmbed)]
#[folder = "../web/dist/turingarena-contest/"]
pub struct WebContent;
