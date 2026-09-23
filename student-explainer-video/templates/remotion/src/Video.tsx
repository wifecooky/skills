import React from "react";
import { AbsoluteFill, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";
import { FONT, PALETTE } from "./theme";
import { END_FRAMES, Scene, TITLE_FRAMES, Track } from "./timeline";
import { Caption } from "./Caption";
import { TitleCard } from "./TitleCard";
import { EndCard } from "./EndCard";
import { Bgm } from "./Bgm";
import { Signature } from "./Signature";
import { SCENES, Placeholder, SceneProps } from "./scenes";

/** Renders one scene; `t` is seconds since the scene's audio started (negative during the lead-in). */
const SceneShell: React.FC<{ scene: Scene }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const lead = scene.audioStartFrame - scene.startFrame;
  const t = (frame - lead) / fps;
  const Comp: React.FC<SceneProps> = SCENES[scene.id] ?? Placeholder;
  return (
    <AbsoluteFill>
      <Comp scene={scene} t={t} />
      <Signature />
      <Caption scene={scene} t={t} />
      <Sequence from={lead} durationInFrames={Math.ceil(scene.durationSeconds * fps)} layout="none">
        <Audio src={staticFile(`narration/${scene.file}`)} />
      </Sequence>
    </AbsoluteFill>
  );
};

export const Video: React.FC<{ track?: Track }> = ({ track }) => (
  <AbsoluteFill style={{ backgroundColor: PALETTE.bg, fontFamily: FONT, color: PALETTE.ink }}>
    <Bgm track={track} />
    <Sequence from={0} durationInFrames={TITLE_FRAMES} name="title">
      <TitleCard />
    </Sequence>
    {track?.scenes.map((scene) => (
      <Sequence key={scene.id} from={TITLE_FRAMES + scene.startFrame} durationInFrames={scene.durationFrames} name={scene.id}>
        <SceneShell scene={scene} />
      </Sequence>
    ))}
    <Sequence from={TITLE_FRAMES + (track?.durationFrames ?? 0)} durationInFrames={END_FRAMES} name="end">
      <EndCard />
    </Sequence>
  </AbsoluteFill>
);
