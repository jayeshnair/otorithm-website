import { WHY } from '../content.ts';

export default function WhyUs() {
  return (
    <section>
      <div className="wrap split">
        <h2 className="h-lg">Built for time zones, not handoffs.</h2>
        <div className="why">
          {WHY.map((w) => (
            <div key={w.title}>
              <h3 className="h-xs">{w.title}</h3>
              <p className="body">{w.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
