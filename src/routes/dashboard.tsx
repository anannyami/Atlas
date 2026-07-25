import { createFileRoute } from "@tanstack/react-router";

import DashboardLayout from "@/components/dashboard/DashboardLayout";
import RepositoryOverview from "@/components/dashboard/RepositoryOverview";
import TechStack from "@/components/dashboard/TechStack";
import ProjectStructure from "@/components/dashboard/ProjectStructure";
import RepositoryHealth from "@/components/dashboard/RepositoryHealth";
import Activity from "@/components/dashboard/Activity";
import ProjectClassification from "@/components/dashboard/ProjectClassification";

export const Route = createFileRoute("/dashboard")({
  component: DashboardPage,
});

function DashboardPage() {
  return (
    <DashboardLayout>
      <RepositoryOverview />
      <TechStack />
      <ProjectStructure />
      <RepositoryHealth />
      <Activity />
      <ProjectClassification />
    </DashboardLayout>
  );
}
