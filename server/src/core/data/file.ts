import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ApiOutputValue } from '../../main/graphql-types';
import { FileContent } from '../files/file-content';

export const fileSchema = gql`
    "File containing multimedia content"
    type File {
        "File name to use, e.g., for downloads"
        name: String!
        "Media type of this file"
        type: String!
        "Content of this file"
        content: FileContent!

        "URL where this file can be downloaded"
        # TODO: add a 'baseUrl' parameter, and make this URL absolute?
        url: String!
    }
`;

export class File implements ApiOutputValue<'File'> {
    constructor(
        readonly name: string,
        readonly language: string | null,
        readonly type: string,
        readonly content: Promise<FileContent>,
        readonly ctx: ApiContext,
    ) {}

    async url() {
        return `/files/${(await this.content).id}/${this.name}`;
    }
}
