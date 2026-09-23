import React from "react";
import { Composition } from "remotion";
import { Video } from "./Video";
import { CONFIG } from "./theme";
import { FPS, TRACKS, totalFrames } from "./timeline";

/** One composition per voice track. With no narration yet, one composition shows only the title and end cards. */
export const RemotionRoot: React.FC = () => {
  const entries = TRACKS.length
    ? TRACKS.map((track) => ({ id: `${CONFIG.id}-${track.voice.replace(/[^A-Za-z0-9-]/g, "")}`, track }))
    : [{ id: CONFIG.id, track: undefined }];
  return (
    <>
      {entries.map((entry) => (
        <Composition
          key={entry.id}
          id={entry.id}
          component={Video}
          durationInFrames={totalFrames(entry.track)}
          fps={FPS}
          width={CONFIG.width}
          height={CONFIG.height}
          defaultProps={{ track: entry.track }}
        />
      ))}
    </>
  );
};
