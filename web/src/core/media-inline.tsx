import { gql } from '@apollo/client';
// @ts-ignore
import TeX from '@matejmazur/react-katex';
import { css } from 'emotion';
import React, { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// @ts-ignore
import { xonokai } from 'react-syntax-highlighter/dist/esm/styles/prism';
// @ts-ignore
import RemarkMathPlugin from 'remark-math';
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

  return (
    <ReactMarkdown
      source={md}
      plugins={[RemarkMathPlugin]}
      renderers={{
        math: (props: { value: string }) => <TeX>{props.value}</TeX>,
        inlineMath: (props: { value: string }) => <TeX>{props.value}</TeX>,
        code: (props: { value: string; language: string }) => (
          <SyntaxHighlighter language={props.language} style={xonokai}>
            {props.value}
          </SyntaxHighlighter>
        ),
      }}
    />
  );
}

export function MediaInline({ data }: FragmentProps<MediaInlineFragment>) {
  switch (data.variant.type) {
    case 'text/markdown':
      return (
        <div
          className={css`
            overflow-y: scroll;
            height: 100%;
          `}
        >
          <div
            className={css`
              padding: 0.75rem;
              max-width: 60rem;
            `}
          >
            <MarkdownMediaInline data={data}></MarkdownMediaInline>
          </div>
        </div>
      );
    default:
      return (
        <iframe
          title="inline-iframe"
          className={css`
            display: block;
            height: 100%;
            width: 100%;
            border: none;
          `}
          src={data.variant.url}
        ></iframe>
      );
  }
}
