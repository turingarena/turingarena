import { gql } from '@apollo/client';

const mimeTypeIcons: Record<string, string> = {
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
