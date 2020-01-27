import { gql } from 'apollo-server-core';
import { Resolvers } from '../../main/resolver-types';
import { FileContent } from '../file-content';

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

export type Media = MediaVariant[];

export interface MediaVariant {
    language?: string;

    name: string;
    type: string;
    content: () => Promise<FileContent>;
}

export interface MediaModelRecord {
    Media: Media;
    MediaFile: MediaVariant;
}

export const mediaResolvers: Resolvers = {
    Media: {
        variant: media => media[0],
    },
    MediaFile: {
        url: async variant => `/files/${(await variant.content()).hash}/${variant.name}`,
    },
};
