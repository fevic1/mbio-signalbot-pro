import { cn } from '@/lib/utils';

interface DragHandleProps {
  onMouseDown: (e: React.MouseEvent) => void;
  onDoubleClick: () => void;
  isVertical?: boolean;
  className?: string;
}

export function DragHandle({
  onMouseDown,
  onDoubleClick,
  isVertical = false,
  className,
}: DragHandleProps) {
  return (
    <div
      onMouseDown={onMouseDown}
      onDoubleClick={onDoubleClick}
      title="Drag to resize • Double-click to reset"
      className={cn(
        'drag-handle group relative flex items-center justify-center',
        isVertical ? 'h-2 cursor-row-resize' : 'w-2 cursor-col-resize',
        className
      )}
    />
  );
}
