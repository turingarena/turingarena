import { gql } from '@apollo/client';
import { IconProp } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import React, { AnchorHTMLAttributes } from 'react';
import { MediaDownloadFragment, FileDownloadFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { displayByteSize } from './byte-size';

const mimeTypeIcons: Record<string, IconProp> = {
  'application/pdf': 'file-pdf',
  'text/plain': 'file-alt',
  'application/gzip': 'file-archive',
  'application/zip': 'file-archive',
};

export const fileDownloadFragment = gql`
  fragment FileDownload on File {
    name
    type
    url
    content {
      size {
        bytes
      }
    }
  }
`;

export const mediaDownloadFragment = gql`
  fragment MediaDownload on Media {
    variant {
      ...FileDownload
    }
  }

  ${fileDownloadFragment}
`;

export function MediaDownload({
  data,
  ...rest
}: FragmentProps<MediaDownloadFragment> & AnchorHTMLAttributes<HTMLAnchorElement> & { text: string }) {
  return <FileDownload data={data.variant} {...rest} />;
}

export function FileDownload({
  data,
  text,
  ...rest
}: FragmentProps<FileDownloadFragment> & AnchorHTMLAttributes<HTMLAnchorElement> & { text?: string }) {
  return (
    <a
      title={`${data.name} (${displayByteSize(data.content.size.bytes)})`}
      download={data.name}
      href={data.url}
      {...rest}
    >
      <FontAwesomeIcon icon={mimeTypeIcons[data.type] ?? 'file'} /> {text ?? data.name}
    </a>
  );
}
