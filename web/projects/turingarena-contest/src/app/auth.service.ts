import { Injectable } from '@angular/core';
import { Apollo } from 'apollo-angular';

export interface Auth {
  token: string;
  userId: string;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  constructor(
    private readonly apollo: Apollo,
  ) { }

  getAuth = (): Auth | undefined => {
    try {
      const authString = localStorage.getItem('auth');

      if (authString === null) { return undefined; }

      return JSON.parse(authString) as Auth;
    } catch (e) {
      localStorage.removeItem('userId');

      return undefined;
    }
  }

  setAuth = async (auth: Auth | undefined) => {
    if (auth === undefined) {
      localStorage.removeItem('auth');
    } else {
      localStorage.setItem('auth', JSON.stringify(auth));
    }

    await this.apollo.getClient().resetStore();
  }
}
