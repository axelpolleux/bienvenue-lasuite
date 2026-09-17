import logo from "../../assets/bienvenue-logo.webp";
import { GRIST_URL } from "../../lib/grist";
import { buildNavItems } from "../../lib/navigation";
import { NavIcon } from "./NavIcon";
import type { Agent, ScreenId } from "../../types";

export interface SidebarProps {
  agent: Agent;
  activeScreen: ScreenId;
  remainingSteps: number;
  onNavigate: (screen: ScreenId) => void;
  onSignOut: () => void;
  onPullGrist?: () => void;
  onPushGrist?: () => void;
  isPullingGrist?: boolean;
  isPushingGrist?: boolean;
  isSyncingGrist?: boolean;
}

interface GristSyncProps {
  onPullGrist?: () => void;
  onPushGrist?: () => void;
  isPullingGrist?: boolean;
  isPushingGrist?: boolean;
}

function PullIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M8 2v8" />
      <path d="m4.5 7 3.5 3.5L11.5 7" />
      <path d="M2.5 13.5h11" />
    </svg>
  );
}

function PushIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M8 10V2" />
      <path d="m4.5 5 3.5-3.5L11.5 5" />
      <path d="M2.5 13.5h11" />
    </svg>
  );
}

function GristSync({
  onPullGrist,
  onPushGrist,
  isPullingGrist = false,
  isPushingGrist = false,
}: GristSyncProps) {
  const isBusy = isPullingGrist || isPushingGrist;

  return (
    <div
      className="bn-sidebar__sync"
      style={{
        padding: "12px 10px",
        borderTop: "1px solid #f0f0f0",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
      }}
    >
      <div
        style={{
          fontSize: "11px",
          textTransform: "uppercase",
          fontWeight: 700,
          color: "var(--bn-color-ink-subtle)",
          letterSpacing: "0.5px",
        }}
      >
        Grist Synchronization
      </div>
      <button
        type="button"
        className="bn-button bn-button--secondary"
        style={{
          minHeight: "36px",
          padding: "8px 12px",
          fontSize: "12.5px",
          justifyContent: "flex-start",
          gap: "8px",
        }}
        disabled={isBusy}
        aria-busy={isPullingGrist}
        onClick={onPullGrist}
        title="Download updates from Grist into Bienvenue"
      >
        {isPullingGrist ? <span className="bn-spinner bn-spinner--dark" aria-hidden="true" /> : <PullIcon />}
        <span>{isPullingGrist ? "Pulling..." : "Pull from Grist"}</span>
      </button>
      <button
        type="button"
        className="bn-button bn-button--secondary"
        style={{
          minHeight: "36px",
          padding: "8px 12px",
          fontSize: "12.5px",
          justifyContent: "flex-start",
          gap: "8px",
        }}
        disabled={isBusy}
        aria-busy={isPushingGrist}
        onClick={onPushGrist}
        title="Upload agent progress to Grist"
      >
        {isPushingGrist ? <span className="bn-spinner bn-spinner--dark" aria-hidden="true" /> : <PushIcon />}
        <span>{isPushingGrist ? "Pushing..." : "Push to Grist"}</span>
      </button>
    </div>
  );
}

/** Desktop navigation rail (hidden below 900px in favour of {@link TabBar}). */
export function Sidebar({
  agent,
  activeScreen,
  remainingSteps,
  onNavigate,
  onSignOut,
  onPullGrist,
  onPushGrist,
  isPullingGrist = false,
  isPushingGrist = false,
  isSyncingGrist = false,
}: SidebarProps) {
  const navItems = buildNavItems(remainingSteps);
  const pulling = isPullingGrist || (isSyncingGrist && !isPushingGrist);
  const pushing = isPushingGrist;

  return (
    <nav aria-label="Main" className="bn-sidebar">
      <div className="bn-sidebar__brand">
        <a
          href="https://lasuite.numerique.gouv.fr/"
          target="_blank"
          rel="noopener noreferrer"
          title="La Suite numérique (new tab)"
          aria-label="La Suite numérique"
          style={{ display: "block" }}
        >
          <img src={logo} alt="Bienvenue à La Suite" className="bn-sidebar__logo" />
        </a>
      </div>

      {navItems.map((item) => (
        <button
          key={item.screen}
          type="button"
          className="bn-nav-item"
          aria-current={item.screen === activeScreen ? "page" : undefined}
          onClick={() => onNavigate(item.screen)}
        >
          <span className="bn-nav-item__icon" aria-hidden="true">
            <NavIcon screen={item.screen} />
          </span>
          <span className="bn-nav-item__label">{item.label}</span>
          {item.count !== null && item.count > 0 && <span className="bn-nav-item__count">{item.count}</span>}
        </button>
      ))}

      <div className="bn-sidebar__spacer" />

      {agent.role === "manager" && (
        <GristSync
          onPullGrist={onPullGrist}
          onPushGrist={onPushGrist}
          isPullingGrist={pulling}
          isPushingGrist={pushing}
        />
      )}

      <div className="bn-sidebar__account">
        <div className="bn-sidebar__account-name">{agent.name}</div>
        <div className="bn-sidebar__account-email">{agent.email}</div>
        <a href={GRIST_URL} target="_blank" rel="noreferrer" className="bn-sidebar__signout">
          Open Grist
        </a>
        <button type="button" className="bn-sidebar__signout" onClick={onSignOut}>
          Sign out
        </button>
      </div>
    </nav>
  );
}
