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
import { ContestProblemSetItemViewAsideComponent } from '../core/contest-problem-set-item-view-aside.component';
import { ContestProblemSetItemViewSubmissionListModalComponent } from '../core/contest-problem-set-item-view-submission-list-modal.component';
import { ContestProblemSetItemViewSubmissionListComponent } from '../core/contest-problem-set-item-view-submission-list.component';
import { ContestViewAsideComponent } from '../core/contest-view-aside.component';
import { ContestViewClockComponent } from '../core/contest-view-clock.component';
import { ContestViewComponent } from '../core/contest-view.component';
import { FeedbackSectionComponent } from '../core/feedback-section.component';
import { FeedbackComponent } from '../core/feedback.component';
import { GradingComponent } from '../core/grading.component';
import { LoginModalComponent } from '../core/login-modal.component';
import { MainViewMessageListModalComponent } from '../core/main-view-message-list-modal.component';
import { MainViewMessageListComponent } from '../core/main-view-message-list.component';
import { MainViewSendMessageComponent } from '../core/main-view-send-message.component';
import { MainViewComponent } from '../core/main-view.component';
import { MainComponent } from '../core/main.component';
import { MediaDownloadComponent } from '../core/media-download.component';
import { MediaInlineComponent } from '../core/media-inline.component';
import { SubmissionModalComponent } from '../core/submission-modal.component';
import { TextPipe } from '../core/text.pipe';
import { TopBarComponent } from '../core/top-bar.component';
import { ValenceDirective } from '../core/valence.directive';
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
    ContestProblemSetItemViewAsideComponent,
    ContestProblemSetItemViewSubmissionListModalComponent,
    ContestProblemSetItemViewSubmissionListComponent,
    SubmissionModalComponent,
    FeedbackComponent,
    FeedbackSectionComponent,
    MediaInlineComponent,
    MediaDownloadComponent,
    GradingComponent,
    TextPipe,
    ValenceDirective,
    ContestViewClockComponent,
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
