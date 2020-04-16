import { gql } from 'apollo-server-core';
import * as fs from 'fs';
import * as path from 'path';
import { AllowNull, BelongsTo, Column, DataType, ForeignKey, PrimaryKey, Table } from 'sequelize-typescript';
import { v4 as UUIDv4 } from 'uuid';
import { ApiObject } from '../main/api';
import { BaseModel } from '../main/base-model';
import { Resolvers } from '../main/resolver-types';
import { FileContent, FileContentApi } from './file-content';

export const fileCollectionSchema = gql`
    type FileCollectionElement {
        path: String!
        content: FileContent!
    }

    type FileCollection {
        uuid: String!
        files: [FileCollectionElement!]!
    }
`;

/**
 * A collection of files, identified by a UUID.
 *
 * NOTE: a collection is immutable, when is created files cannot be added/removed.
 */
@Table({ timestamps: false, tableName: 'file_collection' })
export class FileCollection extends BaseModel<FileCollection> {
    @PrimaryKey
    @Column(DataType.UUIDV4)
    uuid!: string;

    @AllowNull(false)
    @ForeignKey(() => FileContent)
    @Column
    contentId!: string;

    /** Path of this file in the contest, e.g. home.md */
    @PrimaryKey
    @Column
    path!: string;

    @BelongsTo(() => FileContent)
    content!: FileContent;
    getContent!: () => Promise<FileContent>;
}

export interface FileCollectionModelRecord {
    FileCollection: {
        uuid: string;
    };
    FileCollectionElement: FileCollection;
}

export class FileCollectionApi extends ApiObject {
    /**
     * Create a new FileCollection from a directory
     *
     * @param directory directory that is the root of the collection
     * @return UUID of the created collection
     */
    async createFileCollection(directory: string) {
        const uuid = UUIDv4();

        console.debug(`CREATING FileCollection uuid = ${uuid}, directory = ${directory}`);

        const addFiles = async (dir: string) => {
            const files = fs.readdirSync(path.join(directory, dir));
            for (const file of files) {
                const relPath = path.join(dir, file);
                if (fs.statSync(path.join(directory, relPath)).isDirectory()) {
                    console.debug(`ADD DIRECTORY ${relPath}`);
                    await addFiles(relPath);
                } else {
                    console.debug(`ADD FILE ${relPath}`);
                    const content = await this.ctx.api(FileContentApi).createFromPath(path.join(directory, relPath));
                    await this.ctx.table(FileCollection).create({
                        uuid,
                        contentId: content.id,
                        path: relPath,
                    });
                }
            }
        };

        await addFiles('');

        return uuid;
    }

    /**
     * Extracts a file collection in a temporary directory.
     * If the collection is already in cache, do nothing.
     *
     * @param uuid UUID of the collection
     */
    async extractFileCollection(uuid: string) {
        const tempDir = path.join(this.ctx.environment.config.cachePath, uuid);

        try {
            if ((await fs.promises.stat(tempDir)).isDirectory()) {
                console.debug(`EXTRACT FILE COLLECTION uuid = ${uuid} RESOLVED BY CACHE`);

                return tempDir;
            }
        } catch {
            // Directory doesn't exist and thus stat fails
        }

        console.debug(`EXTRACT FILE COLLECTION uuid = ${uuid} INTO ${tempDir}`);

        const collection = await this.ctx.table(FileCollection).findAll({ where: { uuid } });

        for (const file of collection) {
            const filePath = path.join(tempDir, file.path);

            console.debug(`EXTRACT FILE hash = ${file.contentId} IN ${filePath}`);

            const content = await this.ctx.api(FileContentApi).byId.load(file.contentId);
            await this.ctx.api(FileContentApi).extract(content, filePath);
        }

        return tempDir;
    }
}

export const fileCollectionResolvers: Resolvers = {
    FileCollection: {
        uuid: f => f.uuid,
        files: ({ uuid }, _, ctx) => ctx.table(FileCollection).findAll({ where: { uuid } }),
    },
    FileCollectionElement: {
        path: f => f.path,
        content: (collection, _, ctx) => ctx.table(FileContent).findOne({ where: { id: collection.contentId } }),
    },
};
