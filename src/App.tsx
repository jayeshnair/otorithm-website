import Navbar from './components/Navbar.tsx';
import Hero from './components/Hero.tsx';
import Services from './components/Services.tsx';
import HowWeWork from './components/HowWeWork.tsx';
import WhyUs from './components/WhyUs.tsx';
import Careers from './components/Careers.tsx';
import Contact from './components/Contact.tsx';
import Footer from './components/Footer.tsx';

export default function App() {
  return (
    <>
      <Navbar />
      <main id="top">
        <Hero />
        <Services />
        <HowWeWork />
        <WhyUs />
        <Careers />
        <Contact />
      </main>
      <Footer />
    </>
  );
}
