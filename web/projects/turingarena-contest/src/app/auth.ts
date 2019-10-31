export interface Auth {
  token: string;
  userId: string;
}

export const getAuth = (): Auth | undefined => {
  try {
    const authString = localStorage.getItem('auth');

    if (authString === null) { return undefined; }

    return JSON.parse(authString) as Auth;
  } catch (e) {
    localStorage.removeItem('userId');

    return undefined;
  }
};

export const setAuth = (auth: Auth | undefined) => {
  if (auth === undefined) {
    localStorage.removeItem('auth');
  } else {
    localStorage.setItem('auth', JSON.stringify(auth));
  }
};
