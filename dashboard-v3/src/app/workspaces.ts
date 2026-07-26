export type Workspace =
  | "trading"
  | "execution"
  | "portfolio"
  | "dca"
  | "markets"
  | "research"
  | "system";


export const WORKSPACES = [
  {
    id: "trading",
    label: "Trading Workspace",
  },
  {
    id: "execution",
    label: "Execution Workspace",
  },
  {
    id: "portfolio",
    label: "Portfolio Workspace",
  },
  {
    id: "dca",
    label: "DCA Engine",
  },
  {
    id: "markets",
    label: "Markets",
  },
  {
    id: "research",
    label: "Research",
  },
  {
    id: "system",
    label: "System",
  },
] as const;
