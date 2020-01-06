import { ComponentRef, Directive, ElementRef, Host, Input, OnChanges, Renderer2 } from '@angular/core';

import { AwardGradingFragment } from '../fragments/__generated__/AwardGradingFragment';

import { gradingAttributes } from './grading-attributes';

@Directive({
  selector: '[appGrading]',
})
export class GradingDirective implements OnChanges {
  @Input()
  appGrading!: AwardGradingFragment;

  @Host()
  host!: ComponentRef<unknown>;

  @Input()
  appGradingNativeElement?: HTMLElement;

  constructor(
    private readonly elementRef: ElementRef,
    private readonly renderer: Renderer2,
  ) { }

  ngOnChanges() {
    const nativeElement = this.appGradingNativeElement !== undefined ? this.appGradingNativeElement : this.elementRef.nativeElement;
    for (const [attr, c] of gradingAttributes) {
      const value = c(this.appGrading);
      if (value !== undefined) {
        this.renderer.setAttribute(nativeElement, attr, value);
      } else {
        this.renderer.removeAttribute(nativeElement, attr);
      }
    }
  }

}
