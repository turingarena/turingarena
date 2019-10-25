import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-relative-time',
  template: `<abbr [title]="time | date">{{ time | relativeTime }}</abbr>`,
})
export class RelativeTimeComponent {
  @Input()
  time!: string;
}
