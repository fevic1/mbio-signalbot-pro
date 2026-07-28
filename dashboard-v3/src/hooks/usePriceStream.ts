import { useState, useEffect, useCallback, useRef } from 'react';

interface PriceData {
  [symbol: string]: string;
}

interface UsePriceStreamOptions {
  watchlistSymbols?: string[];
  reconnectDelay?: number;
  maxReconnectDelay?: number;
}

export function usePriceStream({
  watchlistSymbols = [],
  reconnectDelay = 1000,
  maxReconnectDelay = 30000,
}: UsePriceStreamOptions = {}) {
  const [prices, setPrices] = useState<PriceData>({});
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const currentDelayRef = useRef(reconnectDelay);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
  }, []);

  const connect = useCallback(() => {
    disconnect();

    try {
      const eventSource = new EventSource('/api/stream/prices');
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setConnected(true);
        setError(null);
        currentDelayRef.current = reconnectDelay;
        console.log('[PriceStream] Connected');
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Filter to watchlist symbols if provided
          if (watchlistSymbols.length > 0) {
            const filteredPrices: PriceData = {};
            watchlistSymbols.forEach(symbol => {
              if (data[symbol]) {
                filteredPrices[symbol] = data[symbol];
              }
            });
            setPrices(filteredPrices);
          } else {
            setPrices(data);
          }
        } catch (err) {
          console.error('[PriceStream] Parse error:', err);
        }
      };

      eventSource.onerror = (err) => {
        console.error('[PriceStream] Error:', err);
        setConnected(false);
        setError('Connection lost, reconnecting...');
        disconnect();

        // Exponential backoff reconnection
        reconnectTimeoutRef.current = setTimeout(() => {
          currentDelayRef.current = Math.min(
            currentDelayRef.current * 2,
            maxReconnectDelay
          );
          connect();
        }, currentDelayRef.current);
      };
    } catch (err) {
      console.error('[PriceStream] Connection error:', err);
      setError('Failed to connect');
      disconnect();
    }
  }, [watchlistSymbols, reconnectDelay, maxReconnectDelay, disconnect]);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { prices, connected, error, reconnect: connect };
}
