import Constellation from './Constellation.tsx';
import GhostLink from './GhostLink.tsx';
import { SERVICES } from '../content.ts';

export default function Services() {
  return (
    <section id="services">
      <div className="wrap">
        <h2 className="h-lg services-head">Three ways we ship.</h2>
        {SERVICES.map((s, i) => (
          <div key={s.label} className={`service${i % 2 === 1 ? ' flip' : ''}`}>
            <div className="service-copy">
              <span className="label">{s.label}</span>
              <h3 className="h">{s.title}</h3>
              <p className="body">{s.body}</p>
              <GhostLink href="#contact">{s.cta}</GhostLink>
            </div>
            <div className="visual" aria-hidden="true">
              <Constellation formation={s.formation} />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
