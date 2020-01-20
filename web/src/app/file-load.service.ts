import { Injectable } from '@angular/core';
import { FileContentInput } from '../../../../__generated__/globalTypes';

@Injectable({
  providedIn: 'root',
})
export class FileLoadService {
  private async toBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = ev => {
        const url = ((ev.target as unknown) as { result: string }).result;
        resolve(url.substring(url.indexOf(',') + 1));
      };

      reader.onerror = ev => {
        reject(ev);
      };

      reader.readAsDataURL(file);
    });
  }

  async loadFileContent(file: File): Promise<FileContentInput> {
    return {
      base64: await this.toBase64(file),
    };
  }
}
