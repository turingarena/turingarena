import { gql, useQuery } from '@apollo/client';
import React, { useEffect } from 'react';
import { MainQuery, MainQueryVariables } from '../generated/graphql-types';
import { useAuth } from '../util/auth';
import { MainView, mainViewFragment } from './main-view';

export function MainLoader() {
  const { auth, restoreAuth, clearAuth } = useAuth();

  useEffect(() => {
    restoreAuth();
  }, [restoreAuth]); // load auth data from local storage when first displayed

  const { loading, error, data, startPolling } = useQuery<MainQuery, MainQueryVariables>(
    gql`
      query Main($username: ID) {
        mainView(username: $username) {
          pendingSubmissions {
            id
          }

          ...MainView
        }
      }

      ${mainViewFragment}
    `,
    {
      variables: { username: auth?.currentAuth?.username ?? null },
      fetchPolicy: 'cache-and-network',
    },
  );

  useEffect(() => {
    if ((data?.mainView.pendingSubmissions?.length ?? 0) > 0) {
      startPolling(500);
    } else {
      startPolling(30000);
    }
  }, [data]);

  if (data === undefined && loading) return <>Loading...</>;
  if (error !== undefined) {
    clearAuth();

    return <>Error! {error.message}</>;
  }
  if (data?.mainView === undefined) return <>No main view!</>;

  return <MainView data={data?.mainView} />;
}
