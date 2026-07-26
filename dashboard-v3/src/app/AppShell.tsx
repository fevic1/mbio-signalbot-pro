import TerminalLayout from "@/layouts/TerminalLayout";

export default function AppShell({
  children,
  active,
  onNavigate,
}: {
  children: React.ReactNode;
  active: string;
  onNavigate: (page: string) => void;
}) {

  return (
    <TerminalLayout
      active={active}
      onNavigate={onNavigate}
    >
      {children}
    </TerminalLayout>
  );
}
