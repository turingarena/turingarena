import { ModelRecord } from '../core';

export type TypeNameOf<T> = T extends { __typename: infer K } ? K : never;
export type Mapper<T> = TypeNameOf<T> extends never
    ? T
    : TypeNameOf<T> extends keyof ModelRecord
    ? ModelRecord[TypeNameOf<T> & keyof ModelRecord]
    : any;
