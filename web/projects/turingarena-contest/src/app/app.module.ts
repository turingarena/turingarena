import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgxFilesizeModule } from 'ngx-filesize';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BypassSanitizerPipe } from './bypass-sanitizer.pipe';
import { GraphQLModule } from './graphql.module';
import { LoginDialogComponent } from './login-dialog/login-dialog.component';
import { RelativeTimeComponent } from './relative-time/relative-time.component';
import { SubmissionDialogComponent } from './submission-dialog/submission-dialog.component';
import { SubmissionListDialogComponent } from './submission-list-dialog/submission-list-dialog.component';
import { SubmitDialogComponent } from './submit-dialog/submit-dialog.component';
import { TextVariantPipe } from './text-variant.pipe';

@NgModule({
  declarations: [
    AppComponent,
    RelativeTimeComponent,
    SubmitDialogComponent,
    SubmissionDialogComponent,
    BypassSanitizerPipe,
    SubmissionListDialogComponent,
    LoginDialogComponent,
    TextVariantPipe,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    GraphQLModule,
    HttpClientModule,
    NgxFilesizeModule,
    NgbModule,
    FontAwesomeModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
  entryComponents: [
    LoginDialogComponent,
  ],
})
export class AppModule { }
