import { ProgressBar } from "../components/onboarding/ProgressBar";
import { TodoList } from "../components/onboarding/TodoList";
import type { UseOnboardingReturn } from "../hooks/useOnboarding";

export interface ChecklistPageProps {
  onboarding: UseOnboardingReturn;
}

/** Full sequential checklist, matching `03-frontend-app.md` section 4.1. */
export function ChecklistPage({ onboarding }: ChecklistPageProps) {
  const { todos, doneCount, totalCount, currentStep, busyTodoId, verifyTodo, toggleTodo, goToScreen } = onboarding;
  const percentage = totalCount > 0 ? Math.round((doneCount / totalCount) * 100) : 0;
  const unlockHint = !currentStep
    ? "Every step is resolved — you can reopen a self-declared step if something changed."
    : currentStep.order === 1
      ? "Step 1 is available now — later steps unlock as you resolve each one."
      : `Step ${currentStep.order} is available now — the steps after it unlock once it is resolved.`;

  return (
    <>
      <div className="bn-card bn-sticky-progress" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", font: "500 13.5px/1.3 var(--bn-font)" }}>
          <span>
            {doneCount} of {totalCount} steps completed
          </span>
          <span style={{ color: "var(--bn-color-primary)" }}>{percentage}%</span>
        </div>
        <ProgressBar percentage={percentage} />
        <p style={{ margin: 0, font: "400 13px/1.55 var(--bn-font)", color: "var(--bn-color-ink-subtle)" }}>{unlockHint}</p>
      </div>

      <TodoList
        todos={todos}
        busyTodoId={busyTodoId}
        onVerify={(todoId) => void verifyTodo(todoId)}
        onToggle={toggleTodo}
        onOpenSignature={() => goToScreen("signature")}
      />
    </>
  );
}
