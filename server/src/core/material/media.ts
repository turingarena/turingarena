import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../../main/resolver-types';
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
    }
`;

export type Media = MediaVariant[];

export interface MediaVariant {
    language?: string;

    name: string;
    type: string;
    content: () => Promise<FileContent>;
}

export const mediaResolvers: ResolversWithModels<{ Media: Media }> = {
    Media: {
        variant: media => media[0],
    },
};
