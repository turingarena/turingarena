import { Component } from '@angular/core';
import { ContestQueryService } from './contest-query.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  constructor(private contestQueryService: ContestQueryService) { }

  title = 'turingarena-contest';
  contestQuery = this.contestQueryService.watch({}, {
    pollInterval: 10000,
  });
}
