import gql from 'graphql-tag';

import { fileFragment } from './file';
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
  }

  ${textFragment}
  ${fileFragment}
`;
