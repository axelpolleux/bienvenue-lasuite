import docsLogo from "../../assets/tools/docs.svg";
import fichiersLogo from "../../assets/tools/fichiers.svg";
import franceTransfertLogo from "../../assets/tools/france-transfert.svg";
import gristLogo from "../../assets/tools/grist.svg";
import tchapLogo from "../../assets/tools/tchap.svg";
import visioLogo from "../../assets/tools/visio.svg";

const SERVICE_LOGOS: Record<string, string> = {
  Docs: docsLogo,
  Tchap: tchapLogo,
  Visio: visioLogo,
  Grist: gristLogo,
  Fichiers: fichiersLogo,
  "France Transfert": franceTransfertLogo,
};

export interface ServiceIconProps {
  name: string;
  size?: number;
}

/** Official La Suite tool marks (lasuite.numerique.gouv.fr), used for shortcuts and the documentation link. */
export function ServiceIcon({ name, size = 20 }: ServiceIconProps) {
  const src = SERVICE_LOGOS[name];
  if (!src) return null;
  return <img src={src} alt="" aria-hidden="true" width={size} height={size} style={{ display: "block" }} />;
}
