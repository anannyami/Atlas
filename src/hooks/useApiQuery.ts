import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/services";

export interface QueryState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  refetch: () => void;
}

/**
 * Minimal query hook wrapping any service call that accepts an AbortSignal.
 * - Runs on mount and whenever any of `deps` change.
 * - Aborts the previous request when re-running or when the component unmounts.
 * - Exposes `refetch()` for retry buttons.
 */
export function useApiQuery<T>(
  fn: (signal: AbortSignal) => Promise<T>,
  deps: ReadonlyArray<unknown> = [],
): QueryState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [nonce, setNonce] = useState(0);
  const controllerRef = useRef<AbortController | null>(null);
  const fnRef = useRef(fn);
  fnRef.current = fn;

  useEffect(() => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    let cancelled = false;
    setLoading(true);
    setError(null);
    fnRef
      .current(controller.signal)
      .then((res) => {
        if (cancelled || controller.signal.aborted) return;
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.code === "aborted") return;
        setError(err instanceof ApiError ? err : new ApiError(String(err), 0, "unknown"));
        setLoading(false);
      });
    return () => {
      cancelled = true;
      controller.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, nonce]);

  const refetch = useCallback(() => setNonce((n) => n + 1), []);

  return { data, loading, error, refetch };
}

/** Manual mutation runner with the same error/abort semantics. */
export function useMutation<TArgs, TResult>(
  fn: (args: TArgs, signal: AbortSignal) => Promise<TResult>,
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const mutate = useCallback(
    async (args: TArgs): Promise<TResult> => {
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      setLoading(true);
      setError(null);
      try {
        return await fn(args, controller.signal);
      } catch (err) {
        if (!(err instanceof ApiError) || err.code !== "aborted") {
          setError(err instanceof ApiError ? err : new ApiError(String(err), 0, "unknown"));
        }
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [fn],
  );

  const cancel = useCallback(() => controllerRef.current?.abort(), []);

  return { mutate, cancel, loading, error };
}
