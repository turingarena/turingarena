// tslint:disable-next-line: no-submodule-imports
import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgxFilesizeModule } from 'ngx-filesize';
import { MarkdownModule } from 'ngx-markdown';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BypassSanitizerPipe } from './bypass-sanitizer.pipe';
import { ContestViewComponent } from './contest-view/contest-view.component';
import { FileVariantPipe } from './file-variant.pipe';
import { GraphQLModule } from './graphql.module';
import { RelativeTimeComponent } from './relative-time/relative-time.component';
import { SubmissionDialogComponent } from './submission-dialog/submission-dialog.component';
import { SubmitDialogComponent } from './submit-dialog/submit-dialog.component';
import { TextVariantPipe } from './text-variant.pipe';

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
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    GraphQLModule,
    HttpClientModule,
    NgxFilesizeModule,
    NgbModule,
    FontAwesomeModule,
    MarkdownModule.forRoot(),
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule { }
