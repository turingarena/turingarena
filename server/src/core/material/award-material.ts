import { gql } from 'apollo-server-core';
import { ResolversWithModels } from '../../main/resolver-types';
import { Award } from '../award';
import { getProblemMetadata } from '../problem-util';
import { Media } from './media';
import { Text } from './text';

export const awardMaterialSchema = gql`
    extend type Award {
        "Name used to identify this award in this problem. Only for admins."
        name: String!
        "Name of this award to display to users."
        title: Text!
        "Possible grades that can be achieved for this award"
        gradeDomain: GradeDomain!
    }
`;

export interface AwardAttachment {
    title: Text;
    media: Media;
}

export const awardMaterialResolvers: ResolversWithModels<{
    Award: Award;
}> = {
    Award: {
        name: ({ index }) => `subtask.${index}`,
        title: ({ index }) => [
            {
                value: `Subtask ${index}`,
            },
        ],
        gradeDomain: async ({ problem, index }, {}, ctx) => {
            const {
                scoring: { subtasks },
            } = await getProblemMetadata(ctx, problem);
            const { max_score: max } = subtasks[index];

            return max > 0
                ? {
                      __typename: 'NumericGradeDomain',
                      max,
                      allowPartial: true, // FIXME
                      decimalPrecision: 0, // FIXME
                  }
                : {
                      __typename: 'BooleanGradeDomain',
                      _: true,
                  };
        },
    },
};
