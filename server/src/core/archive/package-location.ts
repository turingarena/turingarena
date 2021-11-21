import { gql } from 'apollo-server-core';
import { Column, Model, PrimaryKey, Table } from 'sequelize-typescript';
import { ApiOutputValue } from '../../main/graphql-types';
import { PackageBranch } from './package-branch';
import { PackageService } from './package-service';
import { PackageTarget } from './package-target';

export const packageLocationSchema = gql`
    type PackageLocation {
        id: String!
        target: PackageTarget!

        name: String!
        path: String!
        branches: [PackageBranch!]!
    }
`;

@Table
export class PackageLocationData extends Model {
    @PrimaryKey
    @Column
    packageId!: string;

    @PrimaryKey
    @Column
    locationName!: string;

    path!: string;
}

export class PackageLocation implements ApiOutputValue<'PackageLocation'> {
    constructor(readonly target: PackageTarget, readonly name: string, readonly path: string) {}

    ctx = this.target.ctx;

    id = `${this.target.id}:${this.name}`;

    async branches() {
        const branchNames = await this.ctx.service(PackageService).getSourceBranches(this.target.id, this.path);

        return branchNames.map(branchName => new PackageBranch(this, branchName));
    }
}
