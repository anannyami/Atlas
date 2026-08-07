import { createFileRoute } from "@tanstack/react-router";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import RepositoryOverview from "@/components/dashboard/RepositoryOverview";
import TechStack from "@/components/dashboard/TechStack";
import RepositoryArchitecture from "@/components/dashboard/RepositoryArchitecture";
import ProjectStructure from "@/components/dashboard/ProjectStructure";
import RepositoryHealth from "@/components/dashboard/RepositoryHealth";
import Activity from "@/components/dashboard/Activity";
import ProjectClassification from "@/components/dashboard/ProjectClassification";
import ChatPanel from "@/components/dashboard/ChatPanel";

export const Route = createFileRoute("/dashboard")({
  component: DashboardPage,
});

function DashboardPage() {
  return (
    <DashboardLayout>
      <RepositoryOverview />
      <TechStack />
      <RepositoryArchitecture />
      <ProjectStructure />
      <RepositoryHealth />
      <Activity />
      <ProjectClassification />
      <ChatPanel />
    </DashboardLayout>
  );
}
