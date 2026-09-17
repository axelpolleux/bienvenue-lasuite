import { SignatureBox } from "../components/onboarding/SignatureBox";
import { SignatureInstructions } from "../components/onboarding/SignatureInstructions";
import type { UseOnboardingReturn } from "../hooks/useOnboarding";

export interface SignaturePageProps {
  onboarding: UseOnboardingReturn;
}

/** Signature step: copy the generated signature, then confirm it (`03-frontend-app.md` section 4.1, step 5). */
export function SignaturePage({ onboarding }: SignaturePageProps) {
  const { agent, profile, signatureAccepted, acceptingSignature, acceptSignature, todos } = onboarding;
  const signatureStep = todos.find((t) => t.validationType === "SIGNATURE");
  const locked = !signatureAccepted && !!signatureStep?.isLocked;

  return (
    <>
      <SignatureBox
        agent={agent}
        profile={profile}
        accepted={signatureAccepted}
        locked={locked}
        accepting={acceptingSignature}
        onAccept={acceptSignature}
      />
      <SignatureInstructions />
    </>
  );
}
