import { ReactNode } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <main className="min-h-screen bg-[#F8F1DF]">
      <div className="mx-auto max-w-7xl px-6 py-10 space-y-12">{children}</div>
    </main>
  );
}
