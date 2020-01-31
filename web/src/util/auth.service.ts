import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  getAuth() {
    return {
      token: null as string | null,
    };
  }
}
