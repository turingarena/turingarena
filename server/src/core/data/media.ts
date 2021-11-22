import { gql } from 'apollo-server-core';
import { ApiOutputValue } from '../../main/graphql-types';
import { File } from './file';

export const mediaSchema = gql`
    """
    Multimedia content meant to be directly consumed by users.
    Examples: statement of problems.
    """
    type Media {
        "File containing the best variant of this content for the given parameters (language, media type)"
        # TODO: specify parameters
        variant: File!
    }
`;

export class Media implements ApiOutputValue<'Media'> {
    constructor(readonly variants: File[]) {}

    variant() {
        return this.variants[0];
    }
}
