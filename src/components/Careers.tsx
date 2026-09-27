import GhostLink from './GhostLink.tsx';
import { CAREERS_EMAIL } from '../content.ts';

export default function Careers() {
  return (
    <section id="careers">
      <div className="wrap careers">
        <h2 className="h-sm">Join the bench.</h2>
        <p className="body">
          We're building a network of senior engineers who want meaningful product work with global teams.
        </p>
        <GhostLink href={`mailto:${CAREERS_EMAIL}`}>Send your profile</GhostLink>
      </div>
    </section>
  );
}
