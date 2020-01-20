import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'fromJson',
})
export class FromJsonPipe implements PipeTransform {

  transform(json: string): unknown {
    return JSON.parse(json);
  }

}
