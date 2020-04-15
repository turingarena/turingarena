import { useState } from 'react';

export function useAsync<T extends any[], U>(operation: (...args: T) => Promise<U>) {
  const [data, setData] = useState<U | undefined>(undefined);
  const [successful, setSuccessful] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | undefined>();

  async function run(...args: T) {
    if (loading) {
      throw new Error(`Cannot invoke a useAsync while loading`);
    }

    setLoading(true);
    setSuccessful(false);
    setError(undefined);

    try {
      const nextData = await operation(...args);
      setData(nextData);
      setSuccessful(true);

      return nextData;
    } catch (e) {
      const nextError = e instanceof Error ? e : new Error(`non-Error thrown: ${e}`);
      setError(nextError);
      throw nextError;
    } finally {
      setLoading(false);
    }
  }

  return [
    (...args: T) => {
      run(...args).catch(e => {});
    },
    { data, successful, loading, error },
  ] as const;
}
