import { Component, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { faTools } from '@fortawesome/free-solid-svg-icons';
import { AgGridAngular } from 'ag-grid-angular';
import { Apollo } from 'apollo-angular';

import { AdminQuery } from './__generated__/AdminQuery';
import { AdminContestantsService } from './admin-contestants.service';
import { adminQuery } from './admin-query';
import { AdminSubmissionsService } from './admin-submissions.service';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss'],
})
export class AdminComponent {

  constructor(
    private readonly apollo: Apollo,
    private readonly contestantsService: AdminContestantsService,
    private readonly submissionsService: AdminSubmissionsService,
    readonly route: ActivatedRoute,
  ) { }

  faTools = faTools;

  @ViewChild('contestantsGrid', { static: false })
  contestantsGrid!: AgGridAngular;

  @ViewChild('submissionsGrid', { static: false })
  submissionsGrid!: AgGridAngular;

  quickFilterText = '';

  adminQuery = this.apollo.watchQuery<AdminQuery>({
    query: adminQuery,
    variables: {},
    pollInterval: 3000,
  });

  contestantsGridModel = this.contestantsService.createGridModel(() => this.contestantsGrid, this.adminQuery);
  submissionsGridModel = this.submissionsService.createGridModel(() => this.submissionsGrid, this.adminQuery);
}
