import { Component, Input, ViewEncapsulation } from '@angular/core';
import gql from 'graphql-tag';
import { MediaInlineFragment } from '../generated/graphql-types';

@Component({
  selector: 'app-media-inline',
  templateUrl: './media-inline.component.html',
  styleUrls: ['./media-inline.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class MediaInlineComponent {
  @Input()
  data!: MediaInlineFragment;
}

export const mediaInlineFragment = gql`
  fragment MediaInline on Media {
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
