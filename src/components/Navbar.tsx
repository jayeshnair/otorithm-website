import { useEffect, useState } from 'react';
import { Lockup } from './LigatureMark.tsx';
import { NAV_LINKS } from '../content.ts';

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);

  const close = () => setOpen(false);

  return (
    <>
      <header className={`nav${scrolled ? ' scrolled' : ''}`}>
        <div className="wrap nav-inner">
          <Lockup />
          <nav className="nav-links" aria-label="Primary">
            {NAV_LINKS.map((l) => (
              <a key={l.href} href={l.href}>
                {l.label}
              </a>
            ))}
          </nav>
          <a href="#contact" className="btn btn-sm nav-cta">
            Book a call
          </a>
          <button
            type="button"
            className="burger"
            aria-label={open ? 'Close menu' : 'Open menu'}
            aria-expanded={open}
            aria-controls="menu"
            onClick={() => setOpen((v) => !v)}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </header>

      <div id="menu" className={`menu${open ? ' open' : ''}`} aria-hidden={!open}>
        {NAV_LINKS.map((l) => (
          <a key={l.href} href={l.href} tabIndex={open ? 0 : -1} onClick={close}>
            {l.label}
          </a>
        ))}
        <a href="#contact" className="btn" tabIndex={open ? 0 : -1} onClick={close}>
          Book a call
        </a>
      </div>
    </>
  );
}
