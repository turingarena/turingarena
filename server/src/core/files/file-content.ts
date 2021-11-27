import { gql } from 'apollo-server-core';
import * as fs from 'fs';
import * as path from 'path';
import * as ssri from 'ssri';
import { ApiOutputValue } from '../../main/graphql-types';

export const fileContentSchema = gql`
    type FileContent {
        id: ID!
        base64: String!
        utf8: String!
    }

    input FileContentInput {
        "Base64-encoded content of the file"
        base64: String!
    }
`;

export class FileContent implements ApiOutputValue<'FileContent'> {
    constructor(readonly data: Buffer) {}

    id = ssri.fromData(this.data).hexDigest();

    base64() {
        return this.data.toString('base64');
    }

    utf8() {
        return this.data.toString('utf8');
    }
}

/**
 * Extract the file to path.
 * Creates necessary directories.
 *
 * @param path file path
 */
export async function extractFile(fileContent: FileContent, filePath: string) {
    await fs.promises.mkdir(path.dirname(filePath), { recursive: true });

    return fs.promises.writeFile(filePath, fileContent.data);
}
