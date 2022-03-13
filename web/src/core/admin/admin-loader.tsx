import { gql, useQuery } from '@apollo/client';
import React, { useEffect } from 'react';
import { AdminQuery, AdminQueryVariables } from '../../generated/graphql-types';
import { AdminView, adminViewFragment } from './admin-view';

export function AdminLoader() {
  const { loading, error, data, startPolling } = useQuery<AdminQuery, AdminQueryVariables>(
    gql`
      query Admin {
        ...AdminView
      }

      ${adminViewFragment}
    `,
    {
      fetchPolicy: 'cache-and-network',
    },
  );

  useEffect(() => {
    startPolling(10000);
  }, [startPolling]);

  if (data === undefined && loading) return <>Loading...</>;
  if (error !== undefined) return <>Error! {error.message}</>;
  if (data === undefined) return <>Admin data not loaded</>;

  return <AdminView data={data} />;
}
