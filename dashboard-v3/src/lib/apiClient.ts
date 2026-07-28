/**
 * API Client with automatic auth token injection
 * Per CODING_STANDARD: Every external call needs timeout, retry, exponential backoff
 */

interface FetchOptions extends RequestInit {
  timeout?: number;
  retries?: number;
  backoffMs?: number;
}

export async function fetchWithAuth<T>(
  url: string,
  options: FetchOptions = {}
): Promise<T> {
  const {
    timeout = 5000,
    retries = 3,
    backoffMs = 1000,
    ...fetchOptions
  } = options;

  let lastError: Error | null = null;
  let currentBackoff = backoffMs;

  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      // Get auth token from localStorage (same as SSE interceptor)
      const token =
        localStorage.getItem('mbio_token') ||
        localStorage.getItem('token') ||
        localStorage.getItem('access_token') ||
        '';

      // Merge headers
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...(fetchOptions.headers || {}),
      };

      // Create AbortController for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(url, {
        ...fetchOptions,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`HTTP ${response.status}: ${errorData.detail || response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      lastError = error as Error;
      console.warn(`[API Client] Attempt ${attempt + 1} failed for ${url}:`, error);

      // Don't retry on auth errors or aborts
      if (error instanceof Error && 
          (error.message.includes('401') || error.message.includes('Not authenticated'))) {
        break;
      }

      // Exponential backoff before retry
      if (attempt < retries - 1) {
        await new Promise(resolve => setTimeout(resolve, currentBackoff));
        currentBackoff *= 2;
      }
    }
  }

  throw lastError || new Error('API request failed');
}
