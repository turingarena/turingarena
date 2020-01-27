import { ModelRecord } from '../core';
import { Scalars } from '../generated/graphql-types';

export type TypeNameOf<T> = T extends { __typename: infer K } ? K : never;
export type Mapper<T> = T extends Scalars[keyof Scalars]
    ? T
    : TypeNameOf<T> extends keyof ModelRecord
    ? ModelRecord[TypeNameOf<T> & keyof ModelRecord]
    : any;
