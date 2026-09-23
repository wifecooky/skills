import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { CONFIG, PALETTE } from "./theme";
import { Frame, Rule, cardBackground, useReveal } from "./Signature";

export const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fadeOut = interpolate(frame, [durationInFrames - fps * 0.8, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });
  const title = useReveal(0.1);
  const author = useReveal(0.5);
  const credits = useReveal(0.9);
  return (
    <AbsoluteFill style={{ background: cardBackground, justifyContent: "center", alignItems: "center", opacity: fadeOut }}>
      <Frame />
      <div style={{ fontSize: 72, fontWeight: 700, color: PALETTE.ink, letterSpacing: 6, ...title }}>{CONFIG.title}</div>
      <div style={{ marginTop: 36 }}>
        <Rule delay={0.3} width={160} />
      </div>
      {CONFIG.author ? (
        <div style={{ marginTop: 36, fontSize: 44, color: PALETTE.ink, letterSpacing: 5, ...author }}>{CONFIG.author}</div>
      ) : null}
      <div style={{ marginTop: 44, display: "flex", flexDirection: "column", gap: 14, alignItems: "center", ...credits }}>
        {CONFIG.credits.map((line) => (
          <div key={line} style={{ fontSize: 30, color: PALETTE.muted, letterSpacing: 1.5 }}>
            {line}
          </div>
        ))}
      </div>
    </AbsoluteFill>
  );
};
