import logo from "../../assets/bienvenue-logo.webp";
import { buildNavItems } from "../../lib/navigation";
import { NavIcon } from "./NavIcon";
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
        <a
          href="https://lasuite.numerique.gouv.fr/"
          target="_blank"
          rel="noopener noreferrer"
          title="La Suite numérique (nouvel onglet)"
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

      <div className="bn-sidebar__account">
        <div className="bn-sidebar__account-name">{agent.name}</div>
        <div className="bn-sidebar__account-email">{agent.email}</div>
        <button type="button" className="bn-sidebar__signout" onClick={onSignOut}>
          Sign out
        </button>
      </div>
    </nav>
  );
}
