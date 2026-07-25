import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import type {
  AnalysisResponse,
  RepositoryInfo,
  StructureAnalysis,
  TechStackAnalysis,
  HealthAnalysis,
  ActivityAnalysis,
  ProjectClassification,
} from "@/types/atlas";

interface AnalysisContextType {
  repository: RepositoryInfo | null;
  structure: StructureAnalysis | null;
  techStack: TechStackAnalysis | null;
  classification: ProjectClassification | null;
  health: HealthAnalysis | null;
  activity: ActivityAnalysis | null;
  tree: RepositoryTree | null;
  setTree: (tree: RepositoryTree) => void;

  loading: boolean;
  error: string | null;

  setAnalysis: (analysis: AnalysisResponse) => void;
  clearAnalysis: () => void;

  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [repository, setRepository] = useState<RepositoryInfo | null>(null);

  const [structure, setStructure] = useState<StructureAnalysis | null>(null);

  const [techStack, setTechStack] = useState<TechStackAnalysis | null>(null);

  const [classification, setClassification] = useState<ProjectClassification | null>(null);

  const [health, setHealth] = useState<HealthAnalysis | null>(null);

  const [activity, setActivity] = useState<ActivityAnalysis | null>(null);

  const [tree, setTree] = useState<RepositoryTree | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState<string | null>(null);

  const [analysis, setAnalysisState] = useState<AnalysisResponse | null>(null);

  const setAnalysis = (analysis: AnalysisResponse) => {
    setRepository(analysis.repository);
    setStructure(analysis.structure);
    setTechStack(analysis.tech_stack);
    setClassification(analysis.classification);
    setHealth(analysis.health);
    setActivity(analysis.activity);
    setAnalysisState(analysis);

    sessionStorage.setItem("atlas-analysis", JSON.stringify(analysis));

    setError(null);
  };

  const clearAnalysis = () => {
    setRepository(null);
    setStructure(null);
    setTechStack(null);
    setClassification(null);
    setHealth(null);
    setActivity(null);
    setTree(null);
    setLoading(false);
    setError(null);
    sessionStorage.removeItem("atlas-analysis");
  };

  return (
    <AnalysisContext.Provider
      value={{
        repository,
        structure,
        techStack,
        classification,
        health,
        activity,

        loading,
        error,

        setAnalysis,
        clearAnalysis,

        setLoading,
        setError,
        tree,
        setTree,
      }}
    >
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  const context = useContext(AnalysisContext);

  if (!context) {
    throw new Error("useAnalysis must be used inside AnalysisProvider.");
  }

  return context;
}
