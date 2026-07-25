import TerminalLayout from "@/layouts/TerminalLayout";

export default function AppShell({
  children
}: {
  children: React.ReactNode
}) {

  return (
    <TerminalLayout>
      {children}
    </TerminalLayout>
  );
}
