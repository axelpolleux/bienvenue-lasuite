import type { ReactNode } from "react";

const STEPS: Array<{ title: string; body: ReactNode }> = [
  {
    title: "Copy your signature from Bienvenue",
    body: (
      <>
        In the <strong>Bienvenue</strong> app, open the <strong>Email signature</strong> tab and click{" "}
        <strong>Copy signature</strong>. Your signature (name, job title, department, email, phone) is now on your
        clipboard — no file to download.
      </>
    ),
  },
  {
    title: "Open Messagerie",
    body: (
      <>
        Go to{" "}
        <a href="https://messagerie.numerique.gouv.fr/home" target="_blank" rel="noopener noreferrer">
          messagerie.numerique.gouv.fr
        </a>{" "}
        and sign in with your institutional account.
      </>
    ),
  },
  {
    title: "Go to Preferences → Signatures",
    body: (
      <>
        Click the <strong>Preferences</strong> tab, then select <strong>Signatures</strong> in the side menu.
      </>
    ),
  },
  {
    title: "Create a new signature",
    body: (
      <>
        Click <strong>New signature</strong>. Choose <strong>Plain text</strong> as the format (your Bienvenue
        signature is plain text — no images or HTML needed).
      </>
    ),
  },
  {
    title: "Paste it in",
    body: (
      <>
        Paste (Ctrl/Cmd + V) the signature you copied in step 1 into the signature editor box. Give it a name if
        prompted (e.g. "Official signature").
      </>
    ),
  },
  {
    title: "Set it as default",
    body: (
      <>
        In <strong>Signature usage</strong>, set this signature as the default for the message types you want (new
        messages, replies, forwards) on your account.
      </>
    ),
  },
  {
    title: "Save and Test it",
    body: (
      <>
        Click <strong>Save</strong> at the top of the page. Now, send yourself a test email to confirm the signature
        appears correctly.
      </>
    ),
  },
];

/** Soft, frosted-blue instructions card explaining how to install the copied signature in Messagerie. */
export function SignatureInstructions() {
  return (
    <section className="bn-info-panel">
      <h3 className="bn-info-panel__title">How to Install Your Email Signature in Messagerie</h3>
      {STEPS.map((step, index) => (
        <div key={step.title} className="bn-info-panel__step">
          <span className="bn-info-panel__step-index" aria-hidden="true">
            {index + 1}
          </span>
          <div className="bn-info-panel__step-body">
            <div className="bn-info-panel__step-title">{step.title}</div>
            {step.body}
          </div>
        </div>
      ))}
    </section>
  );
}
