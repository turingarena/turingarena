import { Component, ViewChild } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { faTools } from '@fortawesome/free-solid-svg-icons';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { AgGridAngular } from 'ag-grid-angular';
import { Apollo } from 'apollo-angular';

import { AdminQuery } from './__generated__/AdminQuery';
import { adminQuery } from './admin-query';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrls: ['./admin.component.scss'],
})
export class AdminComponent {

  constructor(
    private readonly apollo: Apollo,
    readonly route: ActivatedRoute,
    readonly modalService: NgbModal,
  ) { }

  faTools = faTools;

  quickFilterText = '';

  adminQuery = this.apollo.watchQuery<AdminQuery>({
    query: adminQuery,
    variables: {},
    pollInterval: 10000,
  });

}
