import { buildNavItems } from "../../lib/navigation";
import type { ScreenId } from "../../types";

export interface TabBarProps {
  activeScreen: ScreenId;
  remainingSteps: number;
  onNavigate: (screen: ScreenId) => void;
}

/** Bottom tab bar shown on narrow viewports instead of {@link Sidebar}. */
export function TabBar({ activeScreen, remainingSteps, onNavigate }: TabBarProps) {
  const navItems = buildNavItems(remainingSteps);

  return (
    <nav aria-label="Main" className="bn-tabbar">
      {navItems.map((item) => (
        <button
          key={item.screen}
          type="button"
          className="bn-tabbar__item"
          aria-current={item.screen === activeScreen ? "page" : undefined}
          onClick={() => onNavigate(item.screen)}
        >
          <span className="bn-tabbar__dot" aria-hidden="true" />
          <span className="bn-tabbar__label">{item.shortLabel}</span>
        </button>
      ))}
    </nav>
  );
}
