import { gql } from 'apollo-server-core';
import { GradeDomain } from '../../generated/graphql-types';
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
    name: string;
    title: Text;
    gradeDomain: GradeDomain;
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
