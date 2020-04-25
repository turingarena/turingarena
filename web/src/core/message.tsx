import { gql } from '@apollo/client';
import React from 'react';
import { MessageFragment } from '../generated/graphql-types';

export const messageFragment = gql`
  fragment Message on Message {
    id
    to
    from
    title
    parent
    content
    meta {
      key
      value
    }
  }
`;

export function Message({ data }: { data: MessageFragment }) {
  return (
    <>
      {data.title !== null && <h2>{data.title}</h2>}
      <p>{data.content}</p>
    </>
  );
}
