import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../../main/resolver-types';
import { AwardMaterial } from './award-material';
import { Media } from './media';
import { Text } from './text';

export const problemMaterialSchema = gql`
    """
    Static content associated to a problem.
    """
    type ProblemMaterial {
        title: Text!
        statement: Media!
        attachments: [ProblemAttachment]!
        awards: [AwardMaterial]!
    }

    type ProblemAttachment {
        title: Text!
        media: Media!
    }
`;

export interface ProblemMaterial {
    title: Text;
    statement: Media;
    attachments: ProblemAttachment[];
    awards: AwardMaterial[];
}

export interface ProblemAttachment {
    title: Text;
    media: Media;
}

export const problemMaterialResolvers: ResolversWithModels<{
    ProblemMaterial: ProblemMaterial;
}> = {
    ProblemMaterial: {},
};
