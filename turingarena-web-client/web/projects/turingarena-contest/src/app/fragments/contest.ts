import gql from 'graphql-tag';

import { fileFragment } from './file';
import { problemViewFragment } from './problem';
import { scoreRangeFragment } from './score';
import { textFragment } from './text';

export const contestMaterialFragment = gql`
  fragment ContestMaterialFragment on ContestMaterial {
    title {
      ...TextFragment
    }
    description {
      ...FileFragment
    }
    attachments {
      title {
        ...TextFragment
      }
      file {
        ...FileFragment
      }
    }
    resources {
      title {
        ...TextFragment
      }
      file {
        ...FileFragment
      }
    }
    startTime
    endTime
  }

  ${textFragment}
  ${fileFragment}
`;
