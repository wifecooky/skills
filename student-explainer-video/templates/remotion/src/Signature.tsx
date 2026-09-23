import React from "react";
import { Easing, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { CONFIG, PALETTE } from "./theme";

const ease = { easing: Easing.out(Easing.cubic), extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };

/** Fade + rise for card elements; `delay` and `length` in seconds. */
export const useReveal = (delay: number, length = 0.7) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const opacity = interpolate(frame, [delay * fps, (delay + length) * fps], [0, 1], ease);
  const y = interpolate(frame, [delay * fps, (delay + length) * fps], [28, 0], ease);
  return { opacity, transform: `translateY(${y}px)` };
};

/** Thin rule that grows from its centre; `width` is its final width in px. */
export const Rule: React.FC<{ delay: number; width?: number }> = ({ delay, width = 120 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scale = interpolate(frame, [delay * fps, (delay + 0.8) * fps], [0, 1], ease);
  return <div style={{ width, height: 2, background: PALETTE.line, opacity: 0.55, transform: `scaleX(${scale})` }} />;
};

/** Hairline inset frame behind title and end cards. */
export const Frame: React.FC = () => (
  <div style={{ position: "absolute", inset: 48, border: `1px solid ${PALETTE.line}`, opacity: 0.22, pointerEvents: "none" }} />
);

/** Small author mark in the top-right corner of every scene; nothing when `author` is empty. */
export const Signature: React.FC = () =>
  CONFIG.author ? (
    <div style={{ position: "absolute", top: 46, right: 64, fontSize: 26, letterSpacing: 2, color: PALETTE.muted, opacity: 0.8 }}>
      {CONFIG.author}
    </div>
  ) : null;

/** Paper background with a faint vignette, shared by the cards. */
export const cardBackground = `radial-gradient(ellipse at 50% 42%, ${PALETTE.bg} 0%, ${PALETTE.bg} 55%, ${PALETTE.fill} 150%)`;
