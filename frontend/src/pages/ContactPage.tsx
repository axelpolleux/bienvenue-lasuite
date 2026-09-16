import { ColleaguesList } from "../components/onboarding/ColleaguesList";
import type { UseOnboardingReturn } from "../hooks/useOnboarding";

export interface ContactPageProps {
  onboarding: UseOnboardingReturn;
}

/** People to reach on Tchap, moved out of Resources into its own tab. */
export function ContactPage({ onboarding }: ContactPageProps) {
  const { colleagues } = onboarding;

  return <ColleaguesList colleagues={colleagues} />;
}
