import { withRows } from "./sprite";

/**
 * Wren: a first-time visitor who has never been to this shop. A green beanie, a
 * travelling jacket with a gold strap, and a folded map held out in one hand.
 * 16 by 24 pixels, drawn for Vanguard in the same style as the other characters.
 */

export const WREN_PALETTE: Record<string, string> = {
  G: "#6fae75", // beanie
  g: "#4f8a57", // beanie band
  R: "#8a5a3c", // hair
  S: "#f2c9a0", // skin
  E: "#1b1f3b", // eyes
  O: "#c0604a", // mouth
  M: "#2e3a5c", // jacket
  m: "#1b1f3b", // jacket shade
  K: "#ffb347", // strap
  P: "#f3e9d2", // map
  p: "#e8743b", // route on the map
  L: "#8fa3bf", // trousers
  B: "#12152a", // boots
};

const IDLE = [
  "......GGGG......",
  ".....GGGGGG.....",
  "....GGGGGGGG....",
  "....gggggggg....",
  "....RSSSSSSR....",
  "....SSSSSSSS....",
  "....SESSSSES....",
  "....SSSSSSSS....",
  "....SSSOOSSS....",
  ".....SSSSSS.....",
  "......SSSS......",
  "...MMMMMMMMMM...",
  "..MMMKMMMMMMMM..",
  "..MMMMKMMMMMMM..",
  "..MMMMMKMMMMMM..",
  "..mMMMMMKMMMPPP.",
  "..SS.MMMMMMSPpP.",
  "....MMMMMMMMPPP.",
  "....LLLLLLLL....",
  "....LLL..LLL....",
  "....LLL..LLL....",
  "....LLL..LLL....",
  "...BBBB..BBBB...",
  "..BBBBB..BBBBB..",
] as const;

export const WREN_FRAMES: Record<string, readonly string[]> = {
  idle: IDLE,
  walk1: withRows(IDLE, { 22: "...BBBB...BBBB..", 23: "..BBBBB........." }),
  walk2: withRows(IDLE, { 22: "..BBBB...BBBB...", 23: ".........BBBBB.." }),
  // Puzzled: the map comes up to the face.
  worry: withRows(IDLE, {
    8: "....SSSOOSSPPP..",
    9: ".....SSSSSSPpP..",
    10: "......SSSS.PPP..",
    15: "..mMMMMMKMMMS...",
    16: "..SS.MMMMMM.....",
    17: "....MMMMMMMM....",
  }),
  // Looking around: eyes to one side.
  fuss: withRows(IDLE, { 6: "....SSESSSSE...." }),
  // Found it: both arms up, map held high.
  happy: withRows(IDLE, {
    9: "PPP..SSSSSS....S",
    10: "PpPS..SSSS.....M",
    11: "PPPMMMMMMMMMMMMM",
    15: "..mMMMMMKMMMMm..",
    16: ".....MMMMMM.....",
    17: "....MMMMMMMM....",
  }),
};
