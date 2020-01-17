// tslint:disable-next-line: no-submodule-imports
import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { RouterModule, Routes } from '@angular/router';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { AgGridModule } from 'ag-grid-angular';
import { NgxFilesizeModule } from 'ngx-filesize';
import { MarkdownModule } from 'ngx-markdown';

import { AdminContestantsComponent } from './admin/admin-contestants/admin-contestants.component';
import { AdminCreateDialogComponent } from './admin/admin-create-dialog/admin-create-dialog.component';
import { AdminEvaluationsComponent } from './admin/admin-evaluations/admin-evaluations.component';
import { AdminMessagesComponent } from './admin/admin-messages/admin-messages.component';
import { AdminProblemsComponent } from './admin/admin-problems/admin-problems.component';
import { AdminSubmissionsComponent } from './admin/admin-submissions/admin-submissions.component';
import { AdminComponent } from './admin/admin.component';
import { AppComponent } from './app.component';
import { ApplyPurePipe } from './apply-pure.pipe';
import { BypassSanitizerPipe } from './bypass-sanitizer.pipe';
import { ContestViewComponent } from './contest-view/contest-view.component';
import { GradingDirective } from './data/grading.directive';
import { GradingComponent } from './data/grading/grading.component';
import { ValenceDirective } from './data/valence.directive';
import { EmptyComponent } from './empty.component';
import { FileVariantPipe } from './file-variant.pipe';
import { FromJsonPipe } from './from-json.pipe';
import { GraphQLModule } from './graphql.module';
import { GridOptionsPipe } from './grid-options.pipe';
import { JsonPurePipe } from './json-pure.pipe';
import { MessageListDialogComponent } from './message-list-dialog/message-list-dialog.component';
import { MessageListComponent } from './message-list/message-list.component';
import { RelativeTimeComponent } from './relative-time/relative-time.component';
import { SubmissionDialogComponent } from './submission-dialog/submission-dialog.component';
import { SubmissionListDialogComponent } from './submission-list-dialog/submission-list-dialog.component';
import { SubmitDialogComponent } from './submit-dialog/submit-dialog.component';
import { TemplateCellRendererComponent } from './template-cell-renderer.component';
import { TextVariantPipe } from './text-variant.pipe';

const routes: Routes = [
  {
    path: '',
    component: ContestViewComponent,
    children: [
      {
        path: '',
        component: EmptyComponent,
      },
      {
        path: 'problem/:problemName',
        component: EmptyComponent,
      },
    ],
  },
  {
    path: 'admin',
    component: AdminComponent,
    children: [
      {
        path: '',
        component: EmptyComponent,
        data: {
          adminSection: '',
        },
      },
      {
        path: 'problems',
        component: EmptyComponent,
        data: {
          adminSection: 'problems',
        },
      },
      {
        path: 'contestants',
        component: EmptyComponent,
        data: {
          adminSection: 'contestants',
        },
      },
      {
        path: 'messages',
        component: EmptyComponent,
        data: {
          adminSection: 'messages',
        },
      },
      {
        path: 'submissions',
        component: EmptyComponent,
        data: {
          adminSection: 'submissions',
        },
      },
      {
        path: 'evaluations',
        component: EmptyComponent,
        data: {
          adminSection: 'evaluations',
        },
      },
    ],
  },
];

@NgModule({
  declarations: [
    AppComponent,
    RelativeTimeComponent,
    SubmitDialogComponent,
    SubmissionDialogComponent,
    BypassSanitizerPipe,
    TextVariantPipe,
    ContestViewComponent,
    FileVariantPipe,
    EmptyComponent,
    AdminComponent,
    AdminCreateDialogComponent,
    GradingComponent,
    GradingDirective,
    ValenceDirective,
    ApplyPurePipe,
    TemplateCellRendererComponent,
    GridOptionsPipe,
    SubmissionListDialogComponent,
    MessageListComponent,
    MessageListDialogComponent,
    AdminSubmissionsComponent,
    FromJsonPipe,
    JsonPurePipe,
    AdminContestantsComponent,
    AdminProblemsComponent,
    AdminEvaluationsComponent,
    AdminMessagesComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    GraphQLModule,
    HttpClientModule,
    NgxFilesizeModule,
    NgbModule,
    FontAwesomeModule,
    MarkdownModule.forRoot(),
    RouterModule.forRoot(routes, {
      enableTracing: true,
      anchorScrolling: 'enabled',
      scrollPositionRestoration: 'enabled',
    }),
    AgGridModule.withComponents([
      TemplateCellRendererComponent,
    ]),
  ],
  providers: [],
  bootstrap: [AppComponent],
  entryComponents: [TemplateCellRendererComponent],
})
export class AppModule { }
