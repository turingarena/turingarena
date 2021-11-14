import { gql } from 'apollo-server-core';
import { ApiContext } from '../../main/api-context';
import { ApiOutputValue } from '../../main/graphql-types';
import { FileContent } from '../files/file-content';

export const mediaSchema = gql`
    """
    Multimedia content meant to be directly consumed by users.
    Examples: statement of problems.
    """
    type Media {
        "File containing the best variant of this content for the given parameters (language, media type)"
        # TODO: specify parameters
        variant: MediaFile!
    }

    "File containing multimedia content"
    type MediaFile {
        "File name to use, e.g., for downloads"
        name: String!
        "Media type of this file"
        type: String!
        "Content of this file"
        content: FileContent!

        "URL where this file can be downloaded"
        # TODO: add a 'baseUrl' parameter, and make this URL absolute?
        url: String!

        # TODO: add integrity?
    }
`;

export class Media {
    constructor(readonly variants: MediaFile[]) {}

    variant() {
        return this.variants[0];
    }
}

export interface MediaModelRecord {
    Media: Media;
    MediaFile: MediaFile;
}

export class MediaFile implements ApiOutputValue<'MediaFile'> {
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
