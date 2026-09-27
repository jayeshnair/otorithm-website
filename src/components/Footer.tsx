import { Lockup } from './LigatureMark.tsx';
import { EMAIL, LINKEDIN_URL } from '../content.ts';

export default function Footer() {
  return (
    <footer>
      <div className="wrap foot">
        <Lockup markSize={22} small />
        <p>
          © 2026 System One Technologies Private Limited. Otorithm is a brand of System One Technologies Pvt Ltd.
        </p>
        <div className="foot-links">
          <a href={LINKEDIN_URL}>LinkedIn</a>
          <a href={`mailto:${EMAIL}`}>Email</a>
        </div>
      </div>
    </footer>
  );
}
