import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { CONFIG, PALETTE } from "./theme";
import { Frame, Rule, cardBackground, useReveal } from "./Signature";

export const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const fadeOut = interpolate(frame, [durationInFrames - fps * 0.4, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });
  const title = useReveal(0.1);
  const subtitle = useReveal(0.4);
  const author = useReveal(0.7);
  return (
    <AbsoluteFill style={{ background: cardBackground, justifyContent: "center", alignItems: "center", opacity: fadeOut }}>
      <Frame />
      <Rule delay={0} />
      <div style={{ marginTop: 40, fontSize: 112, fontWeight: 800, color: PALETTE.ink, letterSpacing: 8, ...title }}>{CONFIG.title}</div>
      {CONFIG.subtitle ? (
        <div style={{ marginTop: 30, fontSize: 44, fontWeight: 400, color: PALETTE.muted, letterSpacing: 3, ...subtitle }}>{CONFIG.subtitle}</div>
      ) : null}
      {CONFIG.author ? (
        <div style={{ position: "absolute", bottom: 88, display: "flex", flexDirection: "column", alignItems: "center", gap: 18, ...author }}>
          <Rule delay={0.7} width={48} />
          <div style={{ fontSize: 32, color: PALETTE.muted, letterSpacing: 4 }}>{CONFIG.author}</div>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
