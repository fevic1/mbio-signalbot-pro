import { useState, useCallback, useEffect } from 'react';
import { useResizable } from '@/hooks/useResizable';
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts';
import { DragHandle } from '@/components/DragHandle';
import { cn } from '@/lib/utils';

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

  const maximizeChart = useCallback(() => {
    setLeftCollapsed(true);
    setRightCollapsed(true);
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
              'panel-transition flex-shrink-0 overflow-hidden',
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
      <div className="flex-1 min-w-0 overflow-hidden">
        {centerPanel}
      </div>

      {/* Right Panel: Visible on desktop, hidden on mobile */}
      {!isMobile && (
        <>
          {/* Right Drag Handle */}
          {!rightCollapsed && (
            <DragHandle
              onMouseDown={rightResizable.handleMouseDown}
              onDoubleClick={rightResizable.handleDoubleClick}
            />
          )}

          <div
            className={cn(
              'panel-transition flex-shrink-0 overflow-hidden',
              rightCollapsed ? 'w-0' : ''
            )}
            style={{ 
              width: rightCollapsed ? '0px' : `${rightResizable.width}px`,
            }}
          >
            {rightPanel}
          </div>
        </>
      )}
    </div>
  );
}
