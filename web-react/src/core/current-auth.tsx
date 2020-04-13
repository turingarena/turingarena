import { gql, useQuery } from '@apollo/client';
import React, { ReactElement } from 'react';
import { CurrentAuthQuery, CurrentAuthQueryVariables } from '../generated/graphql-types';

export const currentAuthQuery = gql`
  query CurrentAuth {
    currentToken @client
    currentUsername @client
  }
`;

export const initialCurrentAuthQueryData: CurrentAuthQuery = {
  __typename: 'Query',
  currentToken: null,
  currentUsername: null,
};

export function CurrentAuthProvider(props: { component: (auth: CurrentAuthQuery) => ReactElement }) {
  const { loading, error, data } = useQuery<CurrentAuthQuery, CurrentAuthQueryVariables>(currentAuthQuery);

  if (data === undefined) return <></>;

  return props.component(data);
}
