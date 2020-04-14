import { useState } from 'react';

export function useAsync<T extends any[], U>(operation: (...args: T) => Promise<U>) {
  const [data, setData] = useState<U | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState();

  return [
    async (...args: T) => {
      if (loading) {
        throw new Error(`Cannot invoke a useAsync while loading`);
      }

      setLoading(true);
      setError(undefined);

      try {
        const nextData = await operation(...args);
        setData(nextData);

        return nextData;
      } catch (nextError) {
        setError(nextError);
        throw nextError;
      } finally {
        setLoading(false);
      }
    },
    { data, loading, error },
  ] as const;
}
