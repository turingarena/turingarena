import { HttpClientModule } from '@angular/common/http'; // tslint:disable-line: no-submodule-imports
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';
import { FaIconLibrary, FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { fas } from '@fortawesome/free-solid-svg-icons';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { AgGridModule } from 'ag-grid-angular';
import { NgxFilesizeModule } from 'ngx-filesize';
import { MarkdownModule } from 'ngx-markdown';
import { AppComponent } from '../core/app.component';
import { ContestProblemAssignmentUserTacklingAsideComponent } from '../core/contest-problem-assignment-user-tackling-aside.component';
import { ContestProblemAssignmentUserTacklingSubmissionListModalComponent } from '../core/contest-problem-assignment-user-tackling-submission-list-modal.component';
import { ContestProblemAssignmentUserTacklingSubmissionListComponent } from '../core/contest-problem-assignment-user-tackling-submission-list.component';
import { ContestProblemAssignmentUserTacklingSubmitModalComponent } from '../core/contest-problem-assignment-user-tackling-submit-modal.component';
import { ContestProblemAssignmentViewAsideComponent } from '../core/contest-problem-assignment-view-aside.component';
import { ContestViewAsideComponent } from '../core/contest-view-aside.component';
import { ContestViewClockComponent } from '../core/contest-view-clock.component';
import { ContestViewComponent } from '../core/contest-view.component';
import { FieldCellRendererComponent } from '../core/data/field-cell-renderer.component';
import { FieldComponent } from '../core/data/field.component';
import { IndexFieldComponent } from '../core/data/index-field.component';
import { MemoryUsageFieldComponent } from '../core/data/memory-usage-field.component';
import { MessageFieldComponent } from '../core/data/message-field.component';
import { TimeUsageFieldComponent } from '../core/data/time-usage-field.component';
import { TitleFieldComponent } from '../core/data/title-field.component';
import { FeedbackSectionComponent } from '../core/feedback/feedback-section.component';
import { FeedbackComponent } from '../core/feedback/feedback.component';
import { ValenceDirective } from '../core/feedback/valence.directive';
import { GradingBooleanComponent } from '../core/grading/fulfillment-field.component';
import { GradingComponent } from '../core/grading/grade-field.component';
import { GradingNumericComponent } from '../core/grading/score-field.component';
import { LoginModalComponent } from '../core/login-modal.component';
import { MainViewComponent } from '../core/main-view.component';
import { MainComponent } from '../core/main.component';
import { MediaDownloadComponent } from '../core/material/media-download.component';
import { MediaInlineComponent } from '../core/material/media-inline.component';
import { TextPipe } from '../core/material/text.pipe';
import { MainViewMessageListModalComponent } from '../core/message/main-view-message-list-modal.component';
import { MainViewMessageListComponent } from '../core/message/main-view-message-list.component';
import { MainViewSendMessageComponent } from '../core/message/main-view-send-message.component';
import { SubmissionModalComponent } from '../core/submission-modal.component';
import { TopBarComponent } from '../core/top-bar.component';
import { ApplyPurePipe } from '../util/apply-pure.pipe';
import { BypassSanitizerPipe } from '../util/bypass-sanitizer.pipe';
import { EmptyComponent } from '../util/empty.component';
import { FromJsonPipe } from '../util/from-json.pipe';
import { GridOptionsPipe } from '../util/grid-options.pipe';
import { JsonPurePipe } from '../util/json-pure.pipe';
import { TemplateCellRendererComponent } from '../util/template-cell-renderer.component';
import { AppRoutingModule } from './app-routing.module';
import { GraphQLModule } from './graphql.module';

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
    TopBarComponent,
    LoginModalComponent,
    MainComponent,
    MainViewComponent,
    MainViewMessageListModalComponent,
    MainViewMessageListComponent,
    MainViewSendMessageComponent,
    ContestViewComponent,
    ContestViewAsideComponent,
    ContestProblemAssignmentViewAsideComponent,
    ContestProblemAssignmentUserTacklingSubmissionListModalComponent,
    ContestProblemAssignmentUserTacklingSubmissionListComponent,
    SubmissionModalComponent,
    FeedbackComponent,
    FeedbackSectionComponent,
    MediaInlineComponent,
    MediaDownloadComponent,
    GradingComponent,
    TextPipe,
    ValenceDirective,
    ContestViewClockComponent,
    GradingBooleanComponent,
    GradingNumericComponent,
    ContestProblemAssignmentUserTacklingSubmitModalComponent,
    ContestProblemAssignmentUserTacklingAsideComponent,
    FieldComponent,
    MemoryUsageFieldComponent,
    TimeUsageFieldComponent,
    MessageFieldComponent,
    TitleFieldComponent,
    IndexFieldComponent,
    FieldCellRendererComponent,
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
export class AppModule /* tslint:disable-line: no-unnecessary-class */ {
  constructor(library: FaIconLibrary) {
    library.addIconPacks(fas);
  }
}
