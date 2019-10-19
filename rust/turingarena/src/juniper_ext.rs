macro_rules! graphql_derive_union_from_enum {
    (
        $( $enum:tt )*
    ) => {
        $( $enum )*
        graphql_union_from_enum! { $( $enum )* }
    };
}

macro_rules! graphql_union_from_enum {
    (
        $( #[ $enum_attr:meta ] )* $vis:vis enum $enum_ident:ident {
            $(
                $( #[ $variant_attr:meta ] )*
                $variant_ident:ident ( $delegate:path )
            ),*

            $( , )?
        }
    ) => {
        $crate::juniper::graphql_union!{
            $enum_ident: () as (stringify!($enum_ident)) where Scalar = <S> |&self| {
                instance_resolvers: |_| {
                    $(
                        &$delegate => match self {
                            $enum_ident::$variant_ident(delegate) => Some(delegate),
                            #[allow(unreachable_patterns)]
                            _ => None,
                        },
                    )*
                }
            }
        }
    };
}

macro_rules! graphql_derive_object_from_unit {
    (
        $( $struct:tt )*
    ) => {
        $( $struct )*
        graphql_object_from_unit! { $( $struct )* }
    };
}

macro_rules! graphql_object_from_unit {
    (
        $( #[ $struct_attr:meta ] )* $vis:vis struct $struct_ident:ident;
    ) => {
        $crate::juniper::graphql_object! {
            $struct_ident: () as (stringify!($struct_ident)) where Scalar = <S> |&self| {
                field ok() -> bool { true }
            }
        }
    };
}
