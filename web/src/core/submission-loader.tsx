import { gql, useQuery } from '@apollo/client';
import React from 'react';
import { SubmissionQuery, SubmissionQueryVariables } from '../generated/graphql-types';
import { Submission, submissionFragment } from './submission';

export function SubmissionLoader({ id }: { id: string }) {
  const { loading, error, data } = useQuery<SubmissionQuery, SubmissionQueryVariables>(
    gql`
      query Submission($id: ID!) {
        submission(id: $id) {
          ...Submission
        }
      }

      ${submissionFragment}
    `,
    {
      variables: { id },
      fetchPolicy: 'cache-and-network',
    },
  );

  if (data === undefined && loading) return <>Loading...</>;
  if (data === undefined) return <>Error! {error?.message ?? 'No data!'}</>;

  return <Submission data={data.submission} />;
}
