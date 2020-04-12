import { gql } from '@apollo/client';
import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { MediaInlineFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';

export const mediaInlineFragment = gql`
  fragment MediaInline on Media {
    variant {
      name
      type
      url
    }
  }
`;

export function MarkdownMediaInline({ data }: FragmentProps<MediaInlineFragment>) {
  const [md, setMd] = useState<string>('');
  const [error, setError] = useState<unknown>();

  useEffect(() => {
    fetch(data.variant.url)
      .then(r => r.text())
      .then(t => {
        setMd(t);
      })
      .catch(e => {
        setError(e);
      });
  }, [data]);

  if (error !== undefined) return <p>Error while loading markdown: {`${error}`}</p>;

  return <ReactMarkdown source={md}></ReactMarkdown>;
}

export function MediaInline({ data }: FragmentProps<MediaInlineFragment>) {
  switch (data.variant.type) {
    case 'text/markdown':
      return <MarkdownMediaInline data={data}></MarkdownMediaInline>;
    default:
      return <iframe className="inline-file-iframe" src={data.variant.url}></iframe>;
  }
}
