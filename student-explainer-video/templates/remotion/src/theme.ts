import config from "../video.config.json";

/** Every colour in the video comes from video.config.json; scenes never hard-code hex values. */
export const CONFIG = config;
export const FONT = config.font;
export const PALETTE = config.palette;
/** Colour of a named object (a, b, c, ...). Unknown names fall back to ink so mistakes are visible, not random. */
export const objectColor = (name: string): string =>
  (PALETTE.objects as Record<string, string>)[name] ?? PALETTE.ink;
