import { useEffect, useRef } from 'react';
import { Constellation as Engine, type Formation } from '../lib/constellation.js';

type Props = { formation: Formation; ambient?: number };

export default function Constellation({ formation, ambient = 0 }: Props) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const engine = new Engine(canvas, {
      formation,
      ambient,
      fill: formation === 'ligature' ? 0.78 : 0.7,
    });
    return () => engine.destroy();
  }, [formation, ambient]);

  return <canvas ref={ref} aria-hidden="true" />;
}
