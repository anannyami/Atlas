import { useEffect, useMemo, useState } from "react";

import { AuthService } from "@/services";
import type { GitHubProfile } from "@/services";

export function initials(name?: string | null) {
  if (!name) return "AT";
  const parts = name.split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "AT";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

export function useAuth() {
  const [user, setUser] = useState<GitHubProfile | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const profile = await AuthService.getCurrentProfile();
        if (active) {
          setUser(profile);
        }
      } catch {
        if (active) {
          setUser(null);
        }
      } finally {
        if (active) {
          setHydrated(true);
        }
      }
    }

    load();
    return () => {
      active = false;
    };
  }, []);

  const disconnect = async () => {
    await AuthService.signOut();
    setUser(null);
  };

  return useMemo(() => ({ user, hydrated, disconnect }), [user, hydrated]);
}
