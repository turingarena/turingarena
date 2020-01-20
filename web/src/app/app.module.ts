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
import { EmptyComponent } from './empty.component';
import { FileVariantPipe } from './file-variant.pipe';
import { FromJsonPipe } from './from-json.pipe';
import { GraphQLModule } from './graphql.module';
import { GridOptionsPipe } from './grid-options.pipe';
import { JsonPurePipe } from './json-pure.pipe';
import { TemplateCellRendererComponent } from './template-cell-renderer.component';
import { TextVariantPipe } from './text-variant.pipe';

@NgModule({
  declarations: [
    AppComponent,
    BypassSanitizerPipe,
    TextVariantPipe,
    FileVariantPipe,
    EmptyComponent,
    ApplyPurePipe,
    TemplateCellRendererComponent,
    GridOptionsPipe,
    FromJsonPipe,
    JsonPurePipe,
  ],
  imports: [
    BrowserModule,
    FormsModule,
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
