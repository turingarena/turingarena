import { gql } from 'apollo-server-core';
import { Column, Model, PrimaryKey, Table } from 'sequelize-typescript';
import { ApiOutputValue } from '../../main/graphql-types';
import { PackageBranch } from './package-branch';
import { PackageTarget } from './package-target';

export const packageLocationSchema = gql`
    type PackageLocation {
        id: String!
        target: PackageTarget!

        name: String!
        path: String!
        branches: [PackageBranch!]!

        mainRevision: PackageRevision
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

    @Column
    path!: string;
}

export class PackageLocation implements ApiOutputValue<'PackageLocation'> {
    constructor(readonly target: PackageTarget, readonly name: string, readonly path: string) {}

    ctx = this.target.ctx;

    id = `${this.target.id}:${this.name}`;

    async branches() {
        const part = this.name === 'default' ? `main` : `location/${this.name}/main`;

        return [part, `${this.target.id}/${part}`].map(branchName => new PackageBranch(this, branchName));
    }

    async mainRevision() {
        const branches = await this.branches();

        for (const branch of branches) {
            const revision = await branch.revision();
            const archive = revision?.archive() ?? null;
            if (archive !== null) return revision;
        }

        return null;
    }
}
