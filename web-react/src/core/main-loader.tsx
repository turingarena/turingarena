import { gql, useQuery } from '@apollo/client';
import React, { useEffect } from 'react';
import { MainQuery, MainQueryVariables } from '../generated/graphql-types';
import { useAuth } from '../util/auth';
import { MainView, mainViewFragment } from './main-view';

export function MainLoader() {
  const { auth, restoreAuth } = useAuth();

  useEffect(() => {
    restoreAuth();
  }, []); // load auth data from local storage when first displayed

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
      variables: { username: auth?.currentAuth?.username ?? null },
      fetchPolicy: 'cache-and-network',
      pollInterval: 30000,
    },
  );

  if (data === undefined && loading) return <>Loading...</>;
  if (error !== undefined) return <>Error! {error.message}</>;
  if (data?.mainView === undefined) return <>No main view!</>;

  return <MainView data={data?.mainView} />;
}
