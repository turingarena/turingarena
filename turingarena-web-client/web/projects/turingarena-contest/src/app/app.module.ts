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

import { AdminCreateDialogComponent } from './admin/admin-create-dialog/admin-create-dialog.component';
import { AdminComponent } from './admin/admin.component';
import { AppComponent } from './app.component';
import { ApplyPurePipe } from './apply-pure.pipe';
import { BypassSanitizerPipe } from './bypass-sanitizer.pipe';
import { ContestViewComponent } from './contest-view/contest-view.component';
import { GradingDirective } from './data/grading.directive';
import { GradingComponent } from './data/grading/grading.component';
import { EmptyComponent } from './empty.component';
import { FileVariantPipe } from './file-variant.pipe';
import { GraphQLModule } from './graphql.module';
import { GridOptionsPipe } from './grid-options.pipe';
import { RelativeTimeComponent } from './relative-time/relative-time.component';
import { SubmissionDialogComponent } from './submission-dialog/submission-dialog.component';
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
        path: 'contestants',
        component: EmptyComponent,
        data: {
          adminSection: 'contestants',
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
    ApplyPurePipe,
    TemplateCellRendererComponent,
    GridOptionsPipe,
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
