import { gql } from 'apollo-server-core';

import { mutationSchema } from './mutation';
import { querySchema } from './query';

export const typeDefs = gql`
  ${querySchema}
  ${mutationSchema}
`;

// tslint:disable-next-line: no-default-export
export default typeDefs; // For graphql-codegen
