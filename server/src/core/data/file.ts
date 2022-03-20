import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ApiOutputValue } from '../../main/graphql-types';
import { FileContent } from '../files/file-content';
import { Text } from './text';

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

    type FileField {
        file: File
    }

    "Column containing a date-time."
    type FileColumn implements TitledColumn {
        title: Text!
        fieldIndex: Int!
    }
`;

export class File implements ApiOutputValue<'File'> {
    constructor(
        readonly name: string,
        readonly language: string | null,
        readonly type: string,
        readonly content: FileContent,
        readonly ctx: ApiContext,
    ) {}

    async url() {
        return `/files/${this.content.id}/${this.name}`;
    }
}

export class FileField implements ApiOutputValue<'FileField'> {
    __typename = 'FileField' as const;

    constructor(readonly file: File | null) {}
}

export class FileColumn implements ApiOutputValue<'FileColumn'> {
    __typename = 'FileColumn' as const;

    constructor(readonly title: Text, readonly fieldIndex: number) {}
}
