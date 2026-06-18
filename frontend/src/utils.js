export const getSignalClass = (signal) => {
  if (!signal) return "signal-Hold";
  if (signal.includes("Buy")) return "signal-Buy";
  if (signal.includes("Avoid")) return "signal-Avoid";
  return "signal-Hold";
};
