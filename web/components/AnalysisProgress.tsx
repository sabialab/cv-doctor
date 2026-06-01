"use client";

import { PROCESSING_STEPS } from "@/lib/constants";

export function AnalysisProgress({ currentStep }: { currentStep?: string | null }) {
  const activeIndex =
    currentStep == null || currentStep === ""
      ? -1
      : PROCESSING_STEPS.findIndex((s) => s.id === currentStep);

  return (
    <ol className="mt-4 space-y-2 text-sm" aria-label="分析进度">
      {PROCESSING_STEPS.map((step, i) => {
        const done = activeIndex >= 0 && i < activeIndex;
        const active = activeIndex >= 0 && i === activeIndex;
        return (
          <li
            key={step.id}
            className={
              active
                ? "font-medium text-neutral-900"
                : done
                  ? "text-neutral-500"
                  : "text-neutral-400"
            }
          >
            {i + 1}. {step.label}
            {active ? " …" : done ? " ✓" : ""}
          </li>
        );
      })}
    </ol>
  );
}
