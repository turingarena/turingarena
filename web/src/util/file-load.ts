import { FileContentInput } from '../generated/graphql-types';

async function toBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = e => {
      const url = ((e.target as unknown) as { result: string }).result;
      resolve(url.substring(url.indexOf(',') + 1));
    };

    reader.onerror = e => {
      reject(e);
    };

    reader.readAsDataURL(file);
  });
}

export async function loadFileContent(file: File): Promise<FileContentInput> {
  return {
    base64: await toBase64(file),
  };
}
