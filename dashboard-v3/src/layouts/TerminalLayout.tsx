export default function TerminalLayout({
  children
}: {
  children: React.ReactNode
}) {

  return (
    <div className="flex min-h-screen">

      <aside className="w-64 border-r p-5">

        <h1 className="font-bold text-lg">
          MBIO SIGNALPRO
        </h1>

        <nav className="mt-8 space-y-3 text-sm">

          <div>
            Trading Workspace
          </div>

          <div>
            Execution Workspace
          </div>

          <div>
            Portfolio Workspace
          </div>

          <div>
            Risk Workspace
          </div>

          <div>
            Research Workspace
          </div>

          <div>
            System Workspace
          </div>

        </nav>

      </aside>


      <main className="flex-1 p-6">

        {children}

      </main>

    </div>
  );
}
