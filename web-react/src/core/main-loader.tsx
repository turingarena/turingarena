import { gql, useQuery } from '@apollo/client';
import React from 'react';
import { CurrentAuthQuery, MainQuery, MainQueryVariables } from '../generated/graphql-types';
import { MainView, mainViewFragment } from './main-view';

export function MainLoader({ currentAuth }: { currentAuth: CurrentAuthQuery }) {
  const { loading, error, data } = useQuery<MainQuery, MainQueryVariables>(
    gql`
      query Main($username: ID) {
        mainView(username: $username) {
          ...MainView
        }
      }

      ${mainViewFragment}
    `,
    {
      variables: { username: currentAuth.currentUsername },
      fetchPolicy: 'cache-and-network',
      pollInterval: 30000,
    },
  );

  if (data === undefined && loading) return <>Loading...</>;
  if (error !== undefined) return <>Error! {error.message}</>;
  if (data?.mainView === undefined) return <>No main view!</>;

  return <MainView data={data?.mainView} />;
}
