import { gql } from '@apollo/client';
import React from 'react';
import { FileFieldFragment } from '../../generated/graphql-types';
import { FragmentProps } from '../../util/fragment-props';
import { FileDownload, fileDownloadFragment } from './media-download';

export const fileFieldFragment = gql`
  fragment FileField on FileField {
    file {
      ...FileDownload
    }
  }

  ${fileDownloadFragment}
`;

export function FileField({ data }: FragmentProps<FileFieldFragment>) {
  const { file } = data;
  if (file === null) return null;
  return <FileDownload data={file} />;
}
