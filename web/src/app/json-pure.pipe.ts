import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'jsonPure',
})
export class JsonPurePipe implements PipeTransform {

  transform(value: unknown): string {
    return JSON.stringify(value);
  }

}
