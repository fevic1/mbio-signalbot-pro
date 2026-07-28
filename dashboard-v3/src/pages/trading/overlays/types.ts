export type OverlayType =
  | "zone"
  | "line"
  | "range"
  | "label";

export type OverlayGroup =
  | "institutional"
  | "ict"
  | "market-profile"
  | "volume"
  | "execution"
  | "risk";

export interface OverlayDefinition {
  id: string;
  name: string;
  type: OverlayType;
  group: OverlayGroup;
  color: string;
  enabled: boolean;

  position?: {
    left?: string;
    top?: string;
    width?: string;
    height?: string;
  };
}
