import type { Formation } from './lib/constellation.js';

// All site copy lives here so it can be edited without touching layout.
export const EMAIL = 'hello@otorithm.com';
export const CAREERS_EMAIL = 'careers@otorithm.com';
export const CAL_LINK = '#contact'; // TODO: replace with your Cal.com booking URL
export const LINKEDIN_URL = '#'; // TODO: company LinkedIn page

export const NAV_LINKS = [
  { label: 'Services', href: '#services' },
  { label: 'How we work', href: '#how' },
  { label: 'Careers', href: '#careers' },
];

export const HERO = {
  label: 'Forward-deployed engineering',
  headline: 'Senior engineers, deployed.',
  body: 'Otorithm embeds senior engineering pods inside your team to ship production software, data platforms and AI. Built in India, working in your time zone.',
};

export const SERVICES: {
  label: string;
  title: string;
  body: string;
  cta: string;
  formation: Formation;
}[] = [
  {
    label: '01 — Engineering pods',
    title: 'Senior pods, embedded in two weeks.',
    body: 'Backend, frontend, data and AI engineers who join your standups, your repos and your roadmap. Monthly engagements, founder-led oversight, and a replacement guarantee.',
    cta: 'Hire a pod',
    formation: 'pods',
  },
  {
    label: '02 — AI transformation',
    title: 'From AI pilot to production.',
    body: 'A two-week readiness sprint, a 30-day agent pilot on your own data, then a production rollout with evals, guardrails and cost controls.',
    cta: 'Start an AI pilot',
    formation: 'ascent',
  },
  {
    label: '03 — Software consulting',
    title: 'Architecture that holds at scale.',
    body: "Platform modernization, event-driven systems, multi-tenant SaaS and payments — reviewed and built by engineers who've run them in production.",
    cta: 'Book an architecture review',
    formation: 'layers',
  },
];

export const STEPS = [
  { title: 'Discover', body: 'A 30-minute call to scope the problem, the stack and the team you need.' },
  { title: 'Match', body: 'Vetted senior profiles within 72 hours. You interview; we stand behind every engineer.' },
  { title: 'Embed', body: 'Engineers join your standups, repos and Slack, with a founder reviewing delivery every week.' },
  { title: 'Scale', body: 'Add, swap or roll off engineers month to month. No lock-in.' },
];

export const WHY = [
  { title: 'Founder-led delivery', body: 'Every engagement has a founder accountable for it.' },
  { title: 'Senior by default', body: 'No one learns on your time.' },
  { title: 'Real overlap', body: 'Near full-day overlap with Europe, and dedicated overlap hours with the US.' },
];
