import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { MediaDownloadFragment } from '../../generated/graphql-types';

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
    'application/pdf': 'file-pdf',
    'text/plain': 'file-alt',
    'application/gzip': 'file-archive',
    'application/zip': 'file-archive',
  };
}

export const mediaDownloadFragment = gql`
  fragment MediaDownload on Media {
    variant {
      name
      type
      url
    }
  }
`;
