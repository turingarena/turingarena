import { gql, useQuery } from '@apollo/client';
import React from 'react';
import { SubmissionQuery, SubmissionQueryVariables } from '../generated/graphql-types';
import { SubmissionModal, submissionModalFragment } from './submission-modal';

export function SubmissionLoader({ id }: { id: string }) {
  const { loading, error, data } = useQuery<SubmissionQuery, SubmissionQueryVariables>(
    gql`
      query Submission($id: ID!) {
        submission(id: $id) {
          ...SubmissionModal
        }
      }

      ${submissionModalFragment}
    `,
    {
      variables: { id },
      fetchPolicy: 'cache-and-network',
      pollInterval: 30000,
    },
  );

  if (data === undefined && loading) return <>Loading...</>;
  if (data === undefined) return <>Error! {error?.message ?? 'No data!'}</>;

  return <SubmissionModal data={data.submission} />;
}
