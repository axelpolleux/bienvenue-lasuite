import logo from "../../assets/bienvenue-logo.png";
import { buildNavItems } from "../../lib/navigation";
import type { Agent, ScreenId } from "../../types";

export interface SidebarProps {
  agent: Agent;
  activeScreen: ScreenId;
  remainingSteps: number;
  onNavigate: (screen: ScreenId) => void;
  onSignOut: () => void;
}

/** Desktop navigation rail (hidden below 900px in favour of {@link TabBar}). */
export function Sidebar({ agent, activeScreen, remainingSteps, onNavigate, onSignOut }: SidebarProps) {
  const navItems = buildNavItems(remainingSteps);

  return (
    <nav aria-label="Main" className="bn-sidebar">
      <div className="bn-sidebar__brand">
        <img src={logo} alt="Bienvenue à La Suite" className="bn-sidebar__logo" />
      </div>

      {navItems.map((item) => (
        <button
          key={item.screen}
          type="button"
          className="bn-nav-item"
          aria-current={item.screen === activeScreen ? "page" : undefined}
          onClick={() => onNavigate(item.screen)}
        >
          <span className="bn-nav-item__dot" aria-hidden="true" />
          <span className="bn-nav-item__label">{item.label}</span>
          {item.count !== null && item.count > 0 && <span className="bn-nav-item__count">{item.count}</span>}
        </button>
      ))}

      <div className="bn-sidebar__spacer" />

      <div className="bn-sidebar__account">
        <div className="bn-sidebar__account-name">{agent.name}</div>
        <div className="bn-sidebar__account-email">{agent.email}</div>
        <div style={{ font: "400 11.5px/1.4 var(--bn-font)", color: "var(--bn-color-ink-subtle)" }}>Role: new agent</div>
        <button type="button" className="bn-sidebar__signout" onClick={onSignOut}>
          Sign out
        </button>
      </div>
    </nav>
  );
}
