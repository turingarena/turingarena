import { ComponentRef, Directive, ElementRef, Host, Input, OnChanges, Renderer2 } from '@angular/core';
import { Valence } from '../../generated/graphql-types';

@Directive({
  selector: '[appValence]',
})
export class ValenceDirective implements OnChanges {
  @Input()
  appValence!: Valence | undefined;

  @Host()
  host!: ComponentRef<unknown>;

  @Input()
  appValenceNativeElement?: HTMLElement;

  constructor(private readonly elementRef: ElementRef, private readonly renderer: Renderer2) {}

  ngOnChanges() {
    const nativeElement =
      this.appValenceNativeElement !== undefined ? this.appValenceNativeElement : this.elementRef.nativeElement;

    const attr = 'data-valence';
    const value = this.appValence;

    if (value !== undefined) {
      this.renderer.setAttribute(nativeElement, attr, value);
    } else {
      this.renderer.removeAttribute(nativeElement, attr);
    }
  }
}
