import { useState, useCallback, useEffect } from 'react';
import { useResizable } from '@/hooks/useResizable';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { DragHandle } from '@/components/DragHandle';
import { cn } from '@/lib/utils';
import { Settings, ChevronLeft, ChevronRight } from 'lucide-react';

interface TradingTerminalProps {
  leftPanel: React.ReactNode;
  centerPanel: React.ReactNode;
  rightPanel: React.ReactNode;
}

export function TradingTerminal({
  leftPanel,
  centerPanel,
  rightPanel,
}: TradingTerminalProps) {
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [rightMinimized, setRightMinimized] = useState(false); // Icon rail mode
  const [isMobile, setIsMobile] = useState(false);

  // Check screen size on mount and resize
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // Dynamic widths based on viewport
  const leftResizable = useResizable({
    initialWidth: Math.min(window.innerWidth * 0.12, 280),
    minWidth: 220,
    maxWidth: 350,
    storageKey: 'trading-left-width',
  });

  const rightResizable = useResizable({
    initialWidth: Math.min(window.innerWidth * 0.16, 340),
    minWidth: 300,
    maxWidth: 400,
    storageKey: 'trading-right-width',
  });

  const toggleLeftPanel = useCallback(() => {
    setLeftCollapsed(prev => !prev);
  }, []);

  const toggleRightPanel = useCallback(() => {
    setRightCollapsed(prev => !prev);
  }, []);

  const minimizeRightPanel = useCallback(() => {
    setRightMinimized(prev => !prev);
  }, []);

  const maximizeChart = useCallback(() => {
    setLeftCollapsed(true);
    setRightCollapsed(true);
    setRightMinimized(false);
  }, []);

  useKeyboardShortcuts({
    toggleLeftPanel,
    toggleRightPanel,
    maximizeChart,
  });

  // On mobile, hide both panels by default
  useEffect(() => {
    if (isMobile) {
      setLeftCollapsed(true);
      setRightCollapsed(true);
    }
  }, [isMobile]);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {/* Left Panel: Visible on desktop, hidden on mobile */}
      {!isMobile && (
        <>
          <div
            className={cn(
              'panel-transition flex-shrink-0 overflow-hidden h-full',
              leftCollapsed ? 'w-0' : ''
            )}
            style={{ 
              width: leftCollapsed ? '0px' : `${leftResizable.width}px`,
            }}
          >
            {leftPanel}
          </div>

          {/* Left Drag Handle */}
          {!leftCollapsed && (
            <DragHandle
              onMouseDown={leftResizable.handleMouseDown}
              onDoubleClick={leftResizable.handleDoubleClick}
            />
          )}
        </>
      )}

      {/* Center Panel: Always visible, takes remaining space */}
      <div className="flex-1 min-w-0 overflow-hidden h-full flex flex-col">
        {centerPanel}
      </div>

      {/* Right Panel: Sliding with icon rail mode */}
      {!isMobile && (
        <>
          {/* Right Drag Handle */}
          {!rightCollapsed && !rightMinimized && (
            <DragHandle
              onMouseDown={rightResizable.handleMouseDown}
              onDoubleClick={rightResizable.handleDoubleClick}
            />
          )}

          {/* Icon Rail (when minimized) */}
          {rightMinimized && (
            <div className="flex-shrink-0 h-full w-12 bg-card border-l border-border flex flex-col items-center py-4 gap-4">
              <button
                onClick={() => setRightMinimized(false)}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Expand QT Parameters"
              >
                <Settings className="h-5 w-5 text-muted-foreground" />
              </button>
              <div className="flex-1" />
              <button
                onClick={() => setRightCollapsed(true)}
                className="p-2 rounded hover:bg-muted transition-colors"
                title="Hide panel"
              >
                <ChevronRight className="h-5 w-5 text-muted-foreground" />
              </button>
            </div>
          )}

          {/* Full Panel */}
          {!rightCollapsed && !rightMinimized && (
            <div
              className={cn(
                'panel-transition flex-shrink-0 overflow-hidden h-full relative',
                rightCollapsed ? 'w-0' : ''
              )}
              style={{ 
                width: rightCollapsed ? '0px' : `${rightResizable.width}px`,
              }}
            >
              {/* Minimize button */}
              <button
                onClick={minimizeRightPanel}
                className="absolute top-3 left-3 z-10 p-1.5 rounded bg-muted/50 hover:bg-muted transition-colors"
                title="Minimize to icon rail"
              >
                <ChevronLeft className="h-3 w-3 text-muted-foreground" />
              </button>
              {rightPanel}
            </div>
          )}
        </>
      )}
    </div>
  );
}
