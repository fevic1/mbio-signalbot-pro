/**
 * SPA Router — History API based
 * Maps URL paths to page modules. Supports back/forward navigation.
 */
import { eventBus } from './event-bus.js';

const _routes = {};
let _currentPage = null;

export function registerRoute(path, pageModule) {
  _routes[path] = pageModule;
}

export function navigateTo(path, pushState = true) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  
  // Resolve route
  const pageModule = _routes[normalizedPath];
  if (!pageModule) {
    console.warn(`[Router] No route registered for: ${normalizedPath}`);
    return;
  }

  // Update URL
  if (pushState && window.location.pathname !== normalizedPath) {
    history.pushState({ path: normalizedPath }, '', normalizedPath);
  }

  // Render page
  const container = document.getElementById('page-container');
  if (!container) return;

  // Cleanup previous page
  if (_currentPage && typeof _currentPage.destroy === 'function') {
    _currentPage.destroy();
  }

  // Mount new page
  container.innerHTML = '';
  _currentPage = pageModule;
  
  if (typeof pageModule.render === 'function') {
    pageModule.render(container);
  } else if (typeof pageModule === 'function') {
    pageModule(container);
  }

  // Notify sidebar
  eventBus.dispatch('nav:change', { path: normalizedPath });
}

export function initRouter() {
  // Handle browser back/forward
  window.addEventListener('popstate', (e) => {
    const path = e.state?.path || '/dashboard';
    navigateTo(path, false);
  });

  // Initial route resolution
  const initialPath = window.location.pathname;
  const resolvedPath = _routes[initialPath] ? initialPath : '/dashboard';
  navigateTo(resolvedPath, false);
}

export function getCurrentPath() {
  return window.location.pathname;
}
