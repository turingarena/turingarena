import { gql } from '@apollo/client';
import { css } from 'emotion';
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

function MediaInlineContent({ data }: FragmentProps<MediaInlineFragment>) {
  switch (data.variant.type) {
    case 'text/markdown':
      return (
        <div
          className={css`
            padding: 0.75rem;
            max-width: 60rem;
          `}
        >
          <MarkdownMediaInline data={data}></MarkdownMediaInline>
        </div>
      );
    default:
      return (
        <iframe
          className={css`
            display: block;
            flex: 1;
            border: none;
          `}
          src={data.variant.url}
        ></iframe>
      );
  }
}

export function MediaInline({ data }: FragmentProps<MediaInlineFragment>) {
  return (
    <div
      className={css`
        display: flex;
        flex: 1;
      `}
    >
      <MediaInlineContent data={data} />
    </div>
  );
}
