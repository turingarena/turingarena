import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { MediaDownloadFragment } from '../generated/graphql-types';

@Component({
  selector: 'app-media-download',
  templateUrl: './media-download.component.html',
  styleUrls: ['./media-download.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class MediaDownloadComponent {
  @Input()
  data!: MediaDownloadFragment;

  mimeTypeIcons = {
    'application/pdf': 'filePdf',
    'text/plain': 'fileAlt',
    'application/gzip': 'fileArchive',
    'application/zip': 'fileArchive',
  };
}

export const mediaDownloadFragment = gql`
  fragment MediaDownload on Media {
    variant {
      name
      type
      content {
        hash
        base64
        utf8
      }
    }
  }
`;
