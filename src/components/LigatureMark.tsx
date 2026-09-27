type Props = { size: number; baseColor?: string };

/** Otorithm Ligature mark: a square "o" whose top edge runs into an amber "t" stem. */
export default function LigatureMark({ size, baseColor = 'var(--paper)' }: Props) {
  return (
    <svg width={size} height={size} viewBox="0 0 120 120" aria-hidden="true" focusable="false">
      <path
        d="M104 48 H16 V96 H60 V48"
        fill="none"
        strokeWidth="12"
        strokeLinejoin="miter"
        style={{ stroke: baseColor }}
      />
      <path d="M84 20 V102" fill="none" strokeWidth="12" style={{ stroke: 'var(--amber)' }} />
    </svg>
  );
}

export function Lockup({ markSize = 28, small = false }: { markSize?: number; small?: boolean }) {
  return (
    <a href="#top" className="lockup" aria-label="Otorithm home">
      <LigatureMark size={markSize} />
      <span className="wordmark" style={small ? { fontSize: 18 } : undefined}>
        otorithm
      </span>
    </a>
  );
}
