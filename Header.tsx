import logo from "../../assets/bienvenue-logo.png";
import { initialsFor } from "../../lib/onboarding";

export interface HeaderProps {
  title: string;
  subtitle: string;
  agentName: string;
}

/** Top app bar: brand mark on mobile, page title, and account avatar. */
export function Header({ title, subtitle, agentName }: HeaderProps) {
  return (
    <header className="bn-header">
      <img src={logo} alt="Bienvenue à La Suite" className="bn-header__logo bn-header__mobile-brand" />
      <div className="bn-header__titles">
        <div className="bn-header__title">{title}</div>
        <div className="bn-header__subtitle">{subtitle}</div>
      </div>
      <div className="bn-header__avatar" aria-hidden="true">
        {initialsFor(agentName)}
      </div>
    </header>
  );
}
