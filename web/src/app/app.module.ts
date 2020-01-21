import { HttpClientModule } from '@angular/common/http'; // tslint:disable-line: no-submodule-imports
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { AgGridModule } from 'ag-grid-angular';
import { NgxFilesizeModule } from 'ngx-filesize';
import { MarkdownModule } from 'ngx-markdown';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ApplyPurePipe } from './apply-pure.pipe';
import { BypassSanitizerPipe } from './bypass-sanitizer.pipe';
import { ContestViewComponent } from './contest-view/contest-view.component';
import { ContestProblemSetItemViewAsideComponent } from './core/contest-problem-set-item-view-aside.component';
import { ContestProblemSetItemViewSubmissionListModalComponent } from './core/contest-problem-set-item-view-submission-list-modal.component';
import { ContestProblemSetItemViewSubmissionListComponent } from './core/contest-problem-set-item-view-submission-list.component';
import { ContestViewAsideComponent } from './core/contest-view-aside.component';
import { FeedbackSectionComponent } from './core/feedback-section.component';
import { FeedbackComponent } from './core/feedback.component';
import { GradingComponent } from './core/grading.component';
import { LoginModalComponent } from './core/login-modal.component';
import { MainMessageListModalComponent } from './core/main-message-list-modal.component';
import { MainMessageListComponent } from './core/main-message-list.component';
import { MainSendMessageFormComponent } from './core/main-send-message-form.component';
import { MainComponent } from './core/main.component';
import { MediaDownloadComponent } from './core/media-download.component';
import { MediaInlineComponent } from './core/media-inline.component';
import { SubmissionModalComponent } from './core/submission-modal.component';
import { TopBarComponent } from './core/top-bar.component';
import { EmptyComponent } from './empty.component';
import { FromJsonPipe } from './from-json.pipe';
import { GraphQLModule } from './graphql.module';
import { GridOptionsPipe } from './grid-options.pipe';
import { JsonPurePipe } from './json-pure.pipe';
import { TemplateCellRendererComponent } from './template-cell-renderer.component';

@NgModule({
  declarations: [
    AppComponent,
    BypassSanitizerPipe,
    EmptyComponent,
    ApplyPurePipe,
    TemplateCellRendererComponent,
    GridOptionsPipe,
    FromJsonPipe,
    JsonPurePipe,
    ContestViewComponent,
    TopBarComponent,
    LoginModalComponent,
    MainComponent,
    MainMessageListModalComponent,
    MainMessageListComponent,
    MainSendMessageFormComponent,
    ContestViewAsideComponent,
    ContestProblemSetItemViewAsideComponent,
    ContestProblemSetItemViewSubmissionListModalComponent,
    ContestProblemSetItemViewSubmissionListComponent,
    SubmissionModalComponent,
    FeedbackComponent,
    FeedbackSectionComponent,
    MediaInlineComponent,
    MediaDownloadComponent,
    GradingComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    GraphQLModule,
    AppRoutingModule,
    NgxFilesizeModule,
    NgbModule,
    FontAwesomeModule,
    MarkdownModule.forRoot(),
    AgGridModule.withComponents([TemplateCellRendererComponent]),
  ],
  providers: [],
  bootstrap: [AppComponent],
  entryComponents: [TemplateCellRendererComponent],
})
export class AppModule {}
