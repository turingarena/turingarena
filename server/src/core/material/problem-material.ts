import { gql } from 'apollo-server-core';
import { Resolvers } from '../../generated/graphql-types';

export const problemMaterialSchema = gql`
    """
    Static content associated to a problem.
    """
    type ProblemMaterial {
        title: Text!
        statement: Media!
        attachments: [ProblemAttachment]!
    }

    type ProblemAttachment {
        title: Text!
        media: Media!
    }
`;

export const problemMaterialResolvers: Resolvers = {};
