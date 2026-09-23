import React from "react";
import { AbsoluteFill } from "remotion";
import { PALETTE } from "../theme";
import { Scene } from "../timeline";

/** `t`: seconds since this scene's audio started. Key visual events to `scene.boundaries[i].startSeconds`. */
export type SceneProps = { scene: Scene; t: number };

/** Register one component per scene id from narration.json. This is the only file the template expects you to change besides the scene files themselves. */
export const SCENES: Record<string, React.FC<SceneProps>> = {};

/** Shown for any scene id without a component, so an unfinished project still renders. */
export const Placeholder: React.FC<SceneProps> = ({ scene }) => (
  <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: 160, textAlign: "center" }}>
    <div style={{ fontSize: 40, color: PALETTE.muted }}>{scene.id}</div>
    <div style={{ marginTop: 24, fontSize: 48, color: PALETTE.ink, lineHeight: 1.5 }}>{scene.text}</div>
  </AbsoluteFill>
);
