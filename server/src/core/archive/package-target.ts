import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ApiOutputValue } from '../../main/graphql-types';
import { PackageLocation, PackageLocationData } from './package-location';

export const packageTargetSchema = gql`
    type PackageTarget {
        id: String!
        locations: [PackageLocation!]!
    }
`;

export class PackageTarget implements ApiOutputValue<'PackageTarget'> {
    constructor(readonly ctx: ApiContext, readonly id: string) {}

    async locations() {
        const locationData = await this.ctx.table(PackageLocationData).findAll({ where: { packageId: this.id } });

        const locations = locationData.map(data => new PackageLocation(this, data.locationName, data.path));

        if (!locations.some(location => location.name === 'default')) {
            // By default, the package x/y/z is found in the directory x/y/z of the repo
            locations.push(new PackageLocation(this, 'default', this.id));
        }

        return locations;
    }
}
