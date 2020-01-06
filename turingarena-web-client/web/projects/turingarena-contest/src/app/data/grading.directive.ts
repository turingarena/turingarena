import { Directive, HostBinding, Input } from '@angular/core';

import { AwardGradingFragment } from '../fragments/__generated__/AwardGradingFragment';
import { getScoreTier, ScoreTier } from '../fragments/score';

@Directive({
  selector: '[appGrading]',
})
export class GradingDirective {
  @Input()
  appGrading!: AwardGradingFragment;

  @HostBinding('attr.data-grading-typename')
  get dataGradingType() {
    return this.appGrading.__typename;
  }

  @HostBinding('attr.data-score-tier')
  get dataScoreTier(): ScoreTier | undefined {
    if (this.appGrading.__typename === 'ScoreAwardGrading') {
      return getScoreTier(this.appGrading);
    }
  }

  @HostBinding('attr.data-badge')
  get dataBadge(): boolean | undefined {
    if (this.appGrading.__typename === 'BadgeAwardGrading') {
      const { grade } = this.appGrading;

      return grade !== null ? grade.value.badge : undefined;
    }
  }
}
