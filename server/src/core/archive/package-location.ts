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

        mainBranch: PackageBranch!
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

    mainBranch() {
        return new PackageBranch(
            this,
            `${this.target.id}/${this.name === 'default' ? `` : `location/${this.name}/`}main`,
        );
    }

    async mainRevision() {
        return this.mainBranch().revision();
    }
}
