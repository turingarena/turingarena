import { gql } from 'apollo-server-core';
import { promises as fs } from 'fs';
import * as pathUtils from 'path';
import { ApiContext } from '../../main/api-context';
import { ApiOutputValue } from '../../main/graphql-types';
import { FileContent } from '../files/file-content';
import { exec2 } from './package-service';

export const packageArchiveSchema = gql`
    type PackageArchive {
        hash: String!
    }
`;

export class PackageArchive implements ApiOutputValue<'PackageArchive'> {
    constructor(readonly ctx: ApiContext, readonly hash: string) {}

    dir = pathUtils.join(this.ctx.config.cachePath, 'archives', this.hash);

    async execInDir(command: string) {
        return exec2(`cd ${this.dir} && { ${command} }`);
    }

    async fileContent(path: string) {
        const cachePath = pathUtils.join(this.dir, path);

        try {
            await fs.access(cachePath);
        } catch {
            return null;
        }

        const data = await fs.readFile(cachePath);

        return new FileContent(data);
    }
}
