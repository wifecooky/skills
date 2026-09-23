import React from "react";
import { interpolate, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";
import { staticFile } from "remotion";
import { CONFIG } from "./theme";
import { TITLE_FRAMES, Track } from "./timeline";

/** Looping background music: fades in over the title card, ducks while narration plays, fades out over the end card. */
export const Bgm: React.FC<{ track?: Track }> = ({ track }) => {
  const { fps, durationInFrames } = useVideoConfig();
  const { file, volume, duck } = CONFIG.bgm;
  if (!file) return null;
  const ramp = Math.round(fps * 0.4);
  const speech = (track?.scenes ?? []).map((s) => [TITLE_FRAMES + s.audioStartFrame, TITLE_FRAMES + s.audioStartFrame + s.durationSeconds * fps]);
  const level = (f: number) => {
    let speaking = 0;
    for (const [s, e] of speech) {
      speaking = Math.max(speaking, interpolate(f, [s - ramp, s, e, e + ramp], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }));
    }
    const fadeIn = interpolate(f, [0, fps], [0, 1], { extrapolateRight: "clamp" });
    const fadeOut = interpolate(f, [durationInFrames - fps * 1.5, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });
    return volume * (1 - speaking * (1 - duck)) * fadeIn * fadeOut;
  };
  return <Audio src={staticFile(file)} loop loopVolumeCurveBehavior="extend" volume={level} />;
};
