import { Component, Input } from '@angular/core';

import { AwardGradingFragment } from '../../fragments/__generated__/AwardGradingFragment';

@Component({
  selector: 'app-grading',
  templateUrl: './grading.component.html',
  styleUrls: ['./grading.component.scss'],
})
export class GradingComponent {
  @Input()
  grading!: AwardGradingFragment;
}
