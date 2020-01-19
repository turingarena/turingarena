import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../../main/resolver-types';
import { Media } from './media';
import { Text } from './text';

export const awardMaterialSchema = gql`
    """
    Static content associated to a problem.
    """
    type AwardMaterial {
        name: String!
        title: Text!
        gradeDomain: GradeDomain!
    }
`;

export interface AwardMaterial {
    title: Text;
    statement: Media;
    attachments: AwardAttachment[];
}

export interface AwardAttachment {
    title: Text;
    media: Media;
}

export const awardMaterialResolvers: ResolversWithModels<{
    AwardMaterial: AwardMaterial;
}> = {
    AwardMaterial: {},
};
