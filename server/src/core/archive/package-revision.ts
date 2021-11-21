import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { PackageArchive } from './package-archive';
import { PackageBranch } from './package-branch';

export const packageRevisionSchema = gql`
    type PackageRevision {
        id: String!
        branch: PackageBranch!

        commitHash: String!
        archive: PackageArchive
    }
`;

export class PackageRevision implements ApiOutputValue<'PackageRevision'> {
    constructor(readonly branch: PackageBranch, readonly commitHash: string, readonly archiveHash: string | null) {}

    ctx = this.branch.ctx;

    id = `${this.branch.id}:${this.commitHash}`;

    archive() {
        if (this.archiveHash === null) return null;

        return new PackageArchive(this.ctx, this.archiveHash);
    }
}
