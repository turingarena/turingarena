import { DocumentNode } from 'graphql';
import * as graphqlTag from 'graphql-tag';

declare module 'graphql-tag' {
  export default function gql(literals: any, ...placeholders: any[]): DocumentNode;
}
