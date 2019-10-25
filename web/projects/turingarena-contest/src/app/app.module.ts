import { HttpClientModule } from '@angular/common/http';
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { NgxFilesizeModule } from 'ngx-filesize';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { GraphQLModule } from './graphql.module';
import { RelativeTimePipe } from './relative-time.pipe';
import { RelativeTimeComponent } from './relative-time/relative-time.component';
import { SubmitDialogComponent } from './submit-dialog/submit-dialog.component';

@NgModule({
  declarations: [
    AppComponent,
    RelativeTimeComponent,
    RelativeTimePipe,
    SubmitDialogComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    GraphQLModule,
    HttpClientModule,
    NgxFilesizeModule,
    NgbModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
  entryComponents: [
    SubmitDialogComponent,
  ]
})
export class AppModule { }
