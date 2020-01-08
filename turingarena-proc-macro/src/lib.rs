extern crate proc_macro;
extern crate proc_macro2;
extern crate syn;

use crate::proc_macro::TokenStream;
use quote::quote;

fn derive_using_macro(input: TokenStream, macro_name: proc_macro2::TokenStream) -> TokenStream {
    let input: syn::Item = syn::parse(input).expect("Invalid syntax");
    let output = quote!(
        #macro_name ! {
            #input
        }
    );
    output.into()
}

#[proc_macro_derive(GraphQLNewtype)]
pub fn newtype_derive(input: TokenStream) -> TokenStream {
    derive_using_macro(input, quote!(graphql_newtype))
}

#[proc_macro_derive(GraphQLObjectFromUnit)]
pub fn object_from_unit_derive(input: TokenStream) -> TokenStream {
    derive_using_macro(input, quote!(graphql_object_from_unit))
}

#[proc_macro_derive(GraphQLUnionFromEnum)]
pub fn union_from_enum_derive(input: TokenStream) -> TokenStream {
    derive_using_macro(input, quote!(graphql_union_from_enum))
}

#[proc_macro_attribute]
pub fn graphql(attr: TokenStream, input: TokenStream) -> TokenStream {
    let input: syn::Item = syn::parse(input).expect("Invalid syntax");
    let attr: proc_macro2::TokenStream = attr.into();
    let output = quote!(
        #[allow(dead_code)]
        #input

        #[juniper::object(#attr)]
        #input
    );
    output.into()
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
