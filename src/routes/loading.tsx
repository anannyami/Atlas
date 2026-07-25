import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "motion/react";

import { AtlasAnalysisService } from "@/services/AtlasAnalysisService";
import { useAnalysis } from "@/context/AnalysisContext";

export const Route = createFileRoute("/loading")({
  validateSearch: (search: Record<string, unknown>) => ({
    repo: typeof search.repo === "string" ? search.repo : "",
  }),
  component: LoadingPage,
});

const ANALYSIS_STEPS = [
  "Validating repository...",
  "Fetching GitHub metadata...",
  "Analyzing project structure...",
  "Detecting technology stack...",
  "Evaluating repository health...",
  "Classifying project...",
  "Preparing dashboard...",
];

function LoadingPage() {
  const navigate = useNavigate();
  const { repo } = Route.useSearch();
  const hasStarted = useRef(false);
  const { setAnalysis, setLoading, setError } = useAnalysis();

  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);

  const repoName = useMemo(() => {
    if (!repo) return "";

    try {
      const url = new URL(repo);
      return url.pathname.replace(/^\/+/, "");
    } catch {
      return repo;
    }
  }, [repo]);

  // Fake progress animation
  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 92) return prev;
        return prev + Math.random() * 6;
      });
    }, 350);

    return () => clearInterval(timer);
  }, []);

  // Step animation
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= ANALYSIS_STEPS.length - 1) return prev;
        return prev + 1;
      });
    }, 900);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (hasStarted.current) return;

    hasStarted.current = true;

    const analyzeRepository = async () => {
      if (!repo) {
        setError("No repository URL provided.");
        navigate({ to: "/" });
        return;
      }

      try {
        setLoading(true);
        setError(null);

        const analysis = await AtlasAnalysisService.analyzeRepository(repo);

        setAnalysis(analysis);

        setProgress(100);
        setCurrentStep(ANALYSIS_STEPS.length - 1);

        await new Promise((resolve) => setTimeout(resolve, 500));

        navigate({
          to: "/dashboard",
        });
      } catch (error) {
        console.error(error);

        setError("Repository analysis failed.");

        navigate({
          to: "/",
        });
      } finally {
        setLoading(false);
      }
    };

    analyzeRepository();
  }, [repo]);

  return (
    <div className="min-h-screen bg-[#F8F1DF] flex items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full max-w-2xl"
      >
        <div className="text-center">
          <p className="uppercase tracking-[0.35em] text-xs text-[#792E3C]/60">Atlas</p>

          <h1 className="mt-4 text-5xl font-serif text-[#5C1E2A]">Analyzing Repository</h1>

          <p className="mt-4 text-lg font-mono text-[#792E3C]">{repoName}</p>

          <p className="mt-2 text-[#792E3C]/70">
            Building an intelligent overview of your project...
          </p>
        </div>

        {/* Progress */}
        <div className="mt-12">
          <div className="flex justify-between mb-2 text-sm text-[#792E3C]/70">
            <span>Analysis Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>

          <div className="h-3 rounded-full bg-[#E7D8B6] overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-[#792E3C]"
              animate={{
                width: `${progress}%`,
              }}
              transition={{
                duration: 0.4,
              }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="mt-10 space-y-4">
          {ANALYSIS_STEPS.map((step, index) => {
            const completed = index < currentStep;
            const active = index === currentStep;

            return (
              <motion.div
                key={step}
                initial={{ opacity: 0, x: -12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.08 }}
                className="flex items-center gap-4"
              >
                {completed ? (
                  <div className="w-7 h-7 rounded-full bg-green-600 text-white flex items-center justify-center text-sm">
                    ✓
                  </div>
                ) : active ? (
                  <motion.div
                    className="w-7 h-7 rounded-full border-2 border-[#C7886B]/40 border-t-[#792E3C]"
                    animate={{ rotate: 360 }}
                    transition={{
                      repeat: Infinity,
                      duration: 0.9,
                      ease: "linear",
                    }}
                  />
                ) : (
                  <div className="w-7 h-7 rounded-full border-2 border-[#D7C4A1]" />
                )}

                <span
                  className={`text-base ${
                    completed || active ? "text-[#5C1E2A]" : "text-[#792E3C]/50"
                  }`}
                >
                  {step}
                </span>
              </motion.div>
            );
          })}
        </div>

        <motion.p
          className="mt-12 text-center text-sm text-[#792E3C]/60"
          animate={{
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            repeat: Infinity,
            duration: 2,
          }}
        >
          This usually takes a few seconds depending on repository size.
        </motion.p>
      </motion.div>
    </div>
  );
}
