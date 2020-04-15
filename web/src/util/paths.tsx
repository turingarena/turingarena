import React, { ReactNode, useContext } from 'react';
import { Route, RouteProps } from 'react-router-dom';

const PathContext = React.createContext<string>('/');

export function useBasePath() {
  return useContext(PathContext);
}

export function SetBasePath({ path, children }: { path: string; children: ReactNode }) {
  return <PathContext.Provider value={path}>{children}</PathContext.Provider>;
}

/** Router for static paths, that also sets the path as base path. */
export function PathRouter({ path, ...rest }: { path: string } & RouteProps) {
  return (
    <SetBasePath path={path}>
      <Route path={path} {...rest} />
    </SetBasePath>
  );
}
