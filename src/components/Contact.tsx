import { useEffect, useState } from 'react';
import { CAL_LINK, EMAIL } from '../content.ts';

export default function Contact() {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return;
    const id = window.setTimeout(() => setCopied(false), 1500);
    return () => window.clearTimeout(id);
  }, [copied]);

  const copy = async () => {
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(EMAIL);
      setCopied(true);
    } catch {
      window.location.href = `mailto:${EMAIL}`;
    }
  };

  return (
    <section id="contact">
      <div className="wrap contact">
        <h2 className="display">What are we building?</h2>
        <div className="actions">
          <a href={CAL_LINK} className="btn">
            Book a call
          </a>
          <button type="button" className="ghost" onClick={copy}>
            <span>{copied ? 'Copied ✓' : EMAIL}</span>
            <svg className="copy-icon" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.2" aria-hidden="true">
              <rect x="3.5" y="3.5" width="7.5" height="7.5" rx="1.2" />
              <path d="M8.5 1H2.2C1.54 1 1 1.54 1 2.2v6.3" />
            </svg>
          </button>
          <span className="sr-only" aria-live="polite">
            {copied ? 'Email address copied to clipboard' : ''}
          </span>
        </div>
      </div>
    </section>
  );
}
