import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { PackageLocation } from './package-location';
import { PackageRevision } from './package-revision';
import { PackageService } from './package-service';

export const packageBranchSchema = gql`
    type PackageBranch {
        id: String!
        location: PackageLocation!

        name: String!
        revision: PackageRevision
    }
`;

export class PackageBranch implements ApiOutputValue<'PackageBranch'> {
    constructor(readonly location: PackageLocation, readonly name: string) {}

    ctx = this.location.ctx;

    id = `${this.location.id}:${this.name}`;

    async revision() {
        const { commitHash, archiveHash } = await this.ctx
            .service(PackageService)
            .checkout(this.name, this.location.path);

        if (commitHash === null) return null;

        return new PackageRevision(this, commitHash, archiveHash);
    }
}
