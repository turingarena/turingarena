pub use turingarena_proc_macro::*;

#[macro_export]
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
        juniper::graphql_union!{
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

#[macro_export]
macro_rules! graphql_object_from_unit {
    (
        $( #[ $struct_attr:meta ] )* $vis:vis struct $struct_ident:ident;
    ) => {
        juniper::graphql_object! {
            $struct_ident: () as (stringify!($struct_ident)) where Scalar = <S> |&self| {
                field ok() -> bool { true }
            }
        }
    };
}

#[macro_export]
macro_rules! graphql_newtype {
    (
        $( #[ $struct_attr:meta ] )* $vis:vis struct $struct_ident:ident($inner_vis:vis $inner:path);
    ) => {
        impl<S> juniper::GraphQLType<S> for $struct_ident
        where
            S: juniper::ScalarValue,
            for<'b> &'b S: juniper::ScalarRefValue<'b>,
            $inner: juniper::GraphQLType<S>,
        {
            type Context = <$inner as juniper::GraphQLType<S>>::Context;
            type TypeInfo = <$inner as juniper::GraphQLType<S>>::TypeInfo;

            fn name(info: &Self::TypeInfo) -> Option<&str> {
                <$inner as juniper::GraphQLType<S>>::name(info)
            }

            fn meta<'r>(
                info: &Self::TypeInfo,
                registry: &mut juniper::Registry<'r, S>,
            ) -> juniper::meta::MetaType<'r, S>
            where
                S: 'r,
            {
                <$inner as juniper::GraphQLType<S>>::meta(info, registry)
            }

            fn resolve_field(
                &self,
                info: &Self::TypeInfo,
                field_name: &str,
                arguments: &juniper::Arguments<S>,
                executor: &juniper::Executor<Self::Context, S>,
            ) -> ::std::result::Result<juniper::Value<S>, juniper::FieldError<S>> {
                <$inner as juniper::GraphQLType<S>>::resolve_field(
                    &self.0, info, field_name, arguments, executor,
                )
            }

            fn resolve_into_type(
                &self,
                info: &Self::TypeInfo,
                type_name: &str,
                selection_set: Option<&[juniper::Selection<S>]>,
                executor: &juniper::Executor<Self::Context, S>,
            ) -> ::std::result::Result<juniper::Value<S>, juniper::FieldError<S>> {
                <$inner as juniper::GraphQLType<S>>::resolve_into_type(
                    &self.0,
                    info,
                    type_name,
                    selection_set,
                    executor,
                )
            }

            fn concrete_type_name(&self, context: &Self::Context, info: &Self::TypeInfo) -> String {
                <$inner as juniper::GraphQLType<S>>::concrete_type_name(&self.0, context, info)
            }

            fn resolve(
                &self,
                info: &Self::TypeInfo,
                selection_set: Option<&[juniper::Selection<S>]>,
                executor: &juniper::Executor<Self::Context, S>,
            ) -> juniper::Value<S> {
                <$inner as juniper::GraphQLType<S>>::resolve(&self.0, info, selection_set, executor)
            }
        }

        impl<S> juniper::FromInputValue<S> for $struct_ident
        where
            $inner: juniper::FromInputValue<S>,
        {
            fn from_input_value(v: &juniper::InputValue<S>) -> Option<Self>
            where
                for<'b> &'b S: juniper::ScalarRefValue<'b>,
            {
                let inner = <$inner as juniper::FromInputValue<S>>::from_input_value(v);
                inner.map(|inner| $struct_ident(inner))
            }
        }

        impl<S> juniper::ToInputValue<S> for $struct_ident
        where
            $inner: juniper::ToInputValue<S>,
        {
            fn to_input_value(&self) -> juniper::InputValue<S> {
                <$inner as juniper::ToInputValue<S>>::to_input_value(&self.0)
            }
        }
    };
}
