import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';

@Pipe({
  name: 'bypassSanitizer',
})
export class BypassSanitizerPipe implements PipeTransform {

  constructor(private readonly sanitizer: DomSanitizer) {}

  transform(value: any, urlType: 'Url' | 'ResourceUrl'): any {
    if (urlType === 'Url') {
      return this.sanitizer.bypassSecurityTrustUrl(value);
    } else {
      return this.sanitizer.bypassSecurityTrustResourceUrl(value);
    }
  }

}
