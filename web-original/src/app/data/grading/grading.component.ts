import { Component, Input } from '@angular/core';
import { AwardGradingFragment } from '../../generated/graphql-types';

@Component({
  selector: 'app-grade-variable',
  templateUrl: './grading.component.html',
  styleUrls: ['./grading.component.scss'],
})
export class GradingComponent {
  @Input()
  grading!: AwardGradingFragment;
}
