import React from "react";
import { CONFIG, PALETTE } from "./theme";
import { Scene, displayText } from "./timeline";

/** The sentence being spoken, from the TTS sentence boundaries. A sentence stays up until the next starts, so a question remains readable during its thinking pause. */
export const Caption: React.FC<{ scene: Scene; t: number }> = ({ scene, t }) => {
  const idx = scene.boundaries.findIndex((b, i) => {
    const next = scene.boundaries[i + 1];
    return t >= b.startSeconds && (!next || t < next.startSeconds);
  });
  if (idx < 0) return null;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: CONFIG.caption.bottom, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          maxWidth: CONFIG.width - 320,
          padding: "16px 44px",
          borderRadius: 14,
          background: PALETTE.ink,
          opacity: 0.88,
          boxShadow: `0 14px 40px ${PALETTE.ink}2E`,
          color: PALETTE.bg,
          fontSize: CONFIG.caption.fontSize,
          lineHeight: 1.35,
          textAlign: "center",
          letterSpacing: 1.5,
        }}
      >
        {displayText(scene.boundaries[idx].text)}
      </div>
    </div>
  );
};

export const SceneTitle: React.FC<{ children: React.ReactNode; color?: string }> = ({ children, color }) => (
  <div style={{ position: "absolute", top: 44, left: 0, right: 0, textAlign: "center", fontSize: 56, fontWeight: 600, color: color ?? PALETTE.ink }}>
    {children}
  </div>
);
