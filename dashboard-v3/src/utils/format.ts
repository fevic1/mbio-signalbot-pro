export const safeToFixed = (value: number | undefined | null, decimals: number = 2): string => {
  if (value === undefined || value === null || isNaN(Number(value))) {
    return '—';
  }
  return Number(value).toFixed(decimals);
};
