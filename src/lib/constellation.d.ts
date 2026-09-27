export type Formation = 'ligature' | 'pods' | 'ascent' | 'layers';

export interface ConstellationOptions {
  formation?: Formation;
  /** Extra ambient particles that drift and never join the formation. */
  ambient?: number;
  /** Share of the canvas's shorter side the formation fills (0–1). */
  fill?: number;
}

/** Each formation is a list of [x, y, width, height, tag?] rects in 120×120 unit space. */
export declare const FORMATIONS: Record<Formation, ReadonlyArray<[number, number, number, number, 'amber'?]>>;

export declare class Constellation {
  constructor(canvas: HTMLCanvasElement, opts?: ConstellationOptions);
  destroy(): void;
}
