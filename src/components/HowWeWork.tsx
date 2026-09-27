import { STEPS } from '../content.ts';

export default function HowWeWork() {
  return (
    <section id="how">
      <div className="wrap split">
        <h2 className="h-lg">How an engagement runs.</h2>
        <ol className="steps">
          {STEPS.map((step, i) => (
            <li key={step.title}>
              <span className="label">{String(i + 1).padStart(2, '0')}</span>
              <h3 className="h-sm">{step.title}</h3>
              <p className="body">{step.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
