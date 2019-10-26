export interface Auth {
  token: string;
  userId: string;
}

export const getAuth = (): Auth => {
  try {
    return JSON.parse(localStorage.getItem('auth')) as Auth;
  } catch (e) {
    localStorage.removeItem('userId');
    return undefined;
  }
};

export const setAuth = (auth: Auth) => {
  localStorage.setItem('auth', JSON.stringify(auth));
};
