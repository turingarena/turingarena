extern crate base64;
extern crate serde;

use serde::{Deserialize, Serialize};

/// Wraps the content of a file, as array of bytes.
#[derive(Serialize, Deserialize, Clone)]
pub struct FileContent(pub Vec<u8>);

// Apparently, we have to define this type in this very generic way,
// to make it usable by other macro-generated types.
// Implementation is "copied" from `juniper_codegen/src/derive_scalar_value.rs`.
impl<S> juniper::GraphQLType<S> for FileContent
where
    S: juniper::ScalarValue,
    for<'b> &'b S: juniper::ScalarRefValue<'b>,
{
    type Context = ();
    type TypeInfo = ();

    fn name(_: &()) -> Option<&'static str> {
        Some("FileContent")
    }

    fn meta<'r>(_: &(), registry: &mut juniper::Registry<'r, S>) -> juniper::meta::MetaType<'r, S>
    where
        S: 'r,
    {
        registry.build_scalar_type::<String>(&()).into_meta()
    }

    fn resolve(
        &self,
        _: &(),
        _: Option<&[juniper::Selection<S>]>,
        _: &juniper::Executor<Self::Context, S>,
    ) -> juniper::Value<S> {
        juniper::Value::from(base64::encode(&self.0))
    }
}
