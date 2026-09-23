import manifest from "../public/narration/manifest.json";
import display from "./captions-display.json";
import { CONFIG } from "./theme";

export type Boundary = { text: string; startSeconds: number; endSeconds: number };
export type Scene = {
  id: string;
  text: string;
  file: string;
  durationSeconds: number;
  startFrame: number;
  durationFrames: number;
  pauseAfterFrames: number;
  audioStartFrame: number;
  boundaries: Boundary[];
};
export type Track = { voice: string; durationFrames: number; scenes: Scene[] };

export const FPS: number = manifest.fps;
export const TRACKS: Track[] = manifest.tracks as Track[];
export const TITLE_FRAMES = Math.round(CONFIG.titleSeconds * FPS);
export const END_FRAMES = Math.round(CONFIG.endSeconds * FPS);
/** Title card, then the narration timeline from narrate.py, then the end card. */
export const totalFrames = (track?: Track) => TITLE_FRAMES + (track?.durationFrames ?? 0) + END_FRAMES;

/** Spoken text → on-screen text (e.g. "A 的平方" → "a²"). */
export const displayText = (spoken: string): string => (display as Record<string, string>)[spoken] ?? spoken;
