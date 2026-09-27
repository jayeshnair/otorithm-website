import type { ReactNode } from 'react';

export default function GhostLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a href={href} className="ghost">
      {children} <span className="arrow" aria-hidden="true">→</span>
    </a>
  );
}
