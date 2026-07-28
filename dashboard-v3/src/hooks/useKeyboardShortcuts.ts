import { useEffect, useCallback } from 'react';

interface KeyboardShortcuts {
  toggleLeftPanel?: () => void;
  toggleRightPanel?: () => void;
  maximizeChart?: () => void;
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcuts) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Ctrl+B: Toggle left panel
      if (e.ctrlKey && e.key === 'b' && !e.shiftKey) {
        e.preventDefault();
        shortcuts.toggleLeftPanel?.();
      }
      
      // Ctrl+Shift+B: Toggle right panel
      if (e.ctrlKey && e.shiftKey && e.key === 'B') {
        e.preventDefault();
        shortcuts.toggleRightPanel?.();
      }
      
      // Space: Maximize chart (only if not in input field)
      if (e.key === ' ' && e.target === document.body) {
        e.preventDefault();
        shortcuts.maximizeChart?.();
      }
    },
    [shortcuts]
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}
