import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ApiOutputValue } from '../../main/graphql-types';

export const packageArchiveSchema = gql`
    type PackageArchive {
        hash: String!
    }
`;

export class PackageArchive implements ApiOutputValue<'PackageArchive'> {
    constructor(readonly ctx: ApiContext, readonly hash: string) {}
}
