import { Component, Input } from '@angular/core';
import { TextFragment } from '../generated/graphql-types';

@Component({
  selector: 'app-top-bar',
  templateUrl: './top-bar.component.html',
  styleUrls: ['./top-bar.component.scss'],
})
export class TopBarComponent {
  @Input()
  title!: TextFragment;
}
