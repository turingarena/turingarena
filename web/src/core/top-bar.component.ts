import { Component, Input, ViewEncapsulation } from '@angular/core';
import { TextFragment } from '../generated/graphql-types';

@Component({
  selector: 'app-top-bar',
  templateUrl: './top-bar.component.html',
  styleUrls: ['./top-bar.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class TopBarComponent {
  @Input()
  title!: TextFragment;
}
