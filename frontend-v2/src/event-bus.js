/**
 * EventBus — Decoupled module communication via CustomEvent
 * 
 * Replaces global variables (_positionsCache, _sortCol, etc.)
 * Modules subscribe only to events they need.
 * Adding new pages/widgets never requires modifying existing modules.
 */

const _bus = new EventTarget();

export const eventBus = {
  /**
   * Dispatch an event with typed data
   * @param {string} event - Event name (e.g., 'sse:overview', 'nav:change')
   * @param {*} detail - Event payload
   */
  dispatch(event, detail) {
    _bus.dispatchEvent(new CustomEvent(event, { detail }));
  },

  /**
   * Subscribe to an event
   * @param {string} event - Event name
   * @param {Function} handler - Callback receiving event.detail
   * @returns {Function} Unsubscribe function
   */
  on(event, handler) {
    const wrapper = (e) => handler(e.detail);
    _bus.addEventListener(event, wrapper);
    return () => _bus.removeEventListener(event, wrapper);
  },

  /**
   * Subscribe to an event once
   */
  once(event, handler) {
    const wrapper = (e) => {
      handler(e.detail);
      _bus.removeEventListener(event, wrapper);
    };
    _bus.addEventListener(event, wrapper);
  },
};
