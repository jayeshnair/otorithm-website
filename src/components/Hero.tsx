import Constellation from './Constellation.tsx';
import GhostLink from './GhostLink.tsx';
import { HERO } from '../content.ts';

export default function Hero() {
  return (
    <section className="hero">
      <div className="wrap hero-grid">
        <div className="hero-copy">
          <span className="label">{HERO.label}</span>
          <h1 className="display">{HERO.headline}</h1>
          <p className="body">{HERO.body}</p>
          <div className="actions">
            <a href="#contact" className="btn">
              Book a call
            </a>
            <GhostLink href="#how">See how we work</GhostLink>
          </div>
        </div>
        <div className="hero-visual" aria-hidden="true">
          <Constellation formation="ligature" ambient={40} />
        </div>
      </div>
    </section>
  );
}
