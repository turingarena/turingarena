import { gql } from '@apollo/client';
import { IconProp } from '@fortawesome/fontawesome-svg-core';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import React from 'react';
import { MediaDownloadFragment } from '../generated/graphql-types';
import { FragmentProps } from '../util/fragment-props';

const mimeTypeIcons: Record<string, IconProp> = {
  'application/pdf': 'file-pdf',
  'text/plain': 'file-alt',
  'application/gzip': 'file-archive',
  'application/zip': 'file-archive',
};

export const mediaDownloadFragment = gql`
  fragment MediaDownload on Media {
    variant {
      name
      type
      url
    }
  }
`;

export function MediaDownload({ data }: FragmentProps<MediaDownloadFragment>) {
  return (
    <a title={data.variant.name} download={data.variant.name} href={data.variant.url}>
      <FontAwesomeIcon icon={mimeTypeIcons[data.variant.type] ?? 'file'} />
      {data.variant.name}
    </a>
  );
}
