import { gql } from 'apollo-server-core';

import { mutationSchema } from './mutation/graphql';
import { querySchema } from './query/graphql';

export const typeDefs = gql`
  ${querySchema}
  ${mutationSchema}
`;

// tslint:disable-next-line: no-default-export
export default typeDefs; // For graphql-codegen
