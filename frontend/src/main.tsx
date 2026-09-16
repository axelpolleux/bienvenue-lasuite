import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles/tokens.css";

/**
 * Entry point. Once `@gouvfr-lasuite/ui-components` is installed (see
 * `03-frontend-app.md` section 3), wrap `<App />` in `<CunninghamProvider
 * currentLocale="fr-FR" theme="default">` here, alongside the Marianne and
 * Material Icons font imports, and remove the hand-rolled tokens in
 * `styles/tokens.css` in favour of `@gouvfr-lasuite/ui-tokens`.
 */
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
