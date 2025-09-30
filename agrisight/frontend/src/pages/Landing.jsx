import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Satellite, Map, BarChart3, AlertTriangle, ShieldCheck, Zap, Leaf, Globe2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';

const Landing = () => {
  const [active, setActive] = useState('');

  useEffect(() => {
    const sections = [
      { id: 'features' },
      { id: 'use-cases' },
      { id: 'pricing' },
      { id: 'faq' },
    ];

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActive(entry.target.id);
          }
        });
      },
      { rootMargin: '-40% 0px -50% 0px', threshold: [0, 0.25, 0.5, 1] }
    );

    sections.forEach(({ id }) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, []);

  const handleNavClick = (e, id) => {
    e.preventDefault();
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActive(id);
      history.replaceState(null, '', `#${id}`);
    }
  };

  return (
    <div className="min-h-screen bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
      {/* Top navigation */}
      <header className="sticky top-0 z-30 w-full border-b border-gray-200/70 bg-white/80 backdrop-blur dark:border-gray-800 dark:bg-gray-950/80">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-green-600">
              <Satellite className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-semibold">AgriSight</span>
          </div>
          <nav className="hidden gap-6 text-sm md:flex">
            <a href="#features" onClick={(e) => handleNavClick(e, 'features')} className={`${active==='features' ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-300'} hover:text-gray-900 dark:hover:text-white`}>Features</a>
            <a href="#use-cases" onClick={(e) => handleNavClick(e, 'use-cases')} className={`${active==='use-cases' ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-300'} hover:text-gray-900 dark:hover:text-white`}>Use cases</a>
            <a href="#pricing" onClick={(e) => handleNavClick(e, 'pricing')} className={`${active==='pricing' ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-300'} hover:text-gray-900 dark:hover:text-white`}>Pricing</a>
            <a href="#faq" onClick={(e) => handleNavClick(e, 'faq')} className={`${active==='faq' ? 'text-gray-900 dark:text-white' : 'text-gray-600 dark:text-gray-300'} hover:text-gray-900 dark:hover:text-white`}>FAQ</a>
          </nav>
          <div className="flex items-center gap-2">
            <Link to="/login"><Button variant="ghost">Log in</Button></Link>
            <Link to="/register"><Button>Try it now</Button></Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden border-b border-gray-200/70 dark:border-gray-800">
        <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-10 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:py-24 lg:px-8">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-green-200 bg-green-50 px-3 py-1 text-xs font-medium text-green-700 dark:border-green-900/50 dark:bg-green-900/20 dark:text-green-300">
              <ShieldCheck className="h-3.5 w-3.5" /> Trusted satellite analytics
            </div>
            <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
              Monitor crop health and risks in near real-time
            </h1>
            <p className="mt-4 max-w-xl text-base text-gray-600 dark:text-gray-300">
              AgriSight turns satellite imagery into clear, actionable insights—helping teams spot stress early, prioritize interventions, and report outcomes with confidence.
            </p>
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <Link to="/register"><Button className="h-11 px-6">Try it now</Button></Link>
              <Link to="/demo"><Button variant="outline" className="h-11 px-6">View demo</Button></Link>
            </div>
            <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">No credit card required. Free trial available.</p>
            <div className="mt-8 grid grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-300 sm:grid-cols-4">
              <div className="flex items-center gap-2"><Leaf className="h-4 w-4 text-green-600" /> NDVI, EVI, NDWI</div>
              <div className="flex items-center gap-2"><AlertTriangle className="h-4 w-4 text-amber-600" /> Stress alerts</div>
              <div className="flex items-center gap-2"><Map className="h-4 w-4 text-sky-600" /> Region tracking</div>
              <div className="flex items-center gap-2"><BarChart3 className="h-4 w-4 text-purple-600" /> Analytics</div>
            </div>
          </div>
          <div>
            <div className="relative rounded-2xl border bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <div className="aspect-[16/10] w-full overflow-hidden rounded-xl">
                <img src="/demo/screenshot-2.svg" alt="Platform map screenshot" className="h-full w-full object-cover" />
              </div>
              <div className="pointer-events-none absolute inset-0 rounded-2xl ring-1 ring-inset ring-black/5 dark:ring-white/5" />
            </div>
          </div>
        </div>
      </section>

      {/* Feature grid */}
      <section id="features" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">Everything you need to act early</h2>
          <p className="mt-3 text-gray-600 dark:text-gray-300">From satellite ingestion to alerting and reports—built for agri teams.</p>
        </div>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { icon: Map, title: 'Interactive map', desc: 'Explore regions, draw AOIs, and overlay indices.' },
            { icon: Leaf, title: 'Vegetation indices', desc: 'NDVI, EVI, NDWI, SAVI with trends and anomalies.' },
            { icon: AlertTriangle, title: 'Stress events', desc: 'Detect abnormal patterns and receive notifications.' },
            { icon: BarChart3, title: 'Analytics', desc: 'Dashboards and charts for performance tracking.' },
            { icon: Globe2, title: 'Satellite data', desc: 'Curated, cloud-filtered scenes from trusted providers.' },
            { icon: Zap, title: 'Fast & reliable', desc: 'Optimized pipeline with retries and transparent status.' },
          ].map((f) => (
            <Card key={f.title}>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-600/10">
                    <f.icon className="h-5 w-5 text-green-700 dark:text-green-300" />
                  </div>
                  <div>
                    <CardTitle className="text-base">{f.title}</CardTitle>
                    <CardDescription>{f.desc}</CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      {/* Screenshot strip */}
      <section className="border-t border-b border-gray-200/70 py-12 dark:border-gray-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-center gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <div className="overflow-hidden rounded-xl border bg-white dark:border-gray-800 dark:bg-gray-900">
              <img src="/demo/screenshot-1.svg" alt="Dashboard screenshot" className="h-full w-full object-cover" />
            </div>
            <div className="overflow-hidden rounded-xl border bg-white dark:border-gray-800 dark:bg-gray-900">
              <img src="/demo/screenshot-2.svg" alt="Map screenshot" className="h-full w-full object-cover" />
            </div>
            <div className="overflow-hidden rounded-xl border bg-white dark:border-gray-800 dark:bg-gray-900">
              <img src="/demo/map-preview.svg" alt="Legend and overlays" className="h-full w-full object-cover" />
            </div>
          </div>
        </div>
      </section>

      {/* Use cases */}
      <section id="use-cases" className="border-t border-b border-gray-200/70 py-16 dark:border-gray-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-start gap-8 lg:grid-cols-3">
            {[
              { title: 'Extension services', desc: 'Target support to farms showing early stress signals.' },
              { title: 'Program M&E', desc: 'Quantify outcomes with consistent, auditable indicators.' },
              { title: 'Risk management', desc: 'Track weather and vegetation anomalies at scale.' },
            ].map((u) => (
              <Card key={u.title}>
                <CardHeader>
                  <CardTitle className="text-lg">{u.title}</CardTitle>
                  <CardDescription>{u.desc}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="list-inside list-disc text-sm text-gray-600 dark:text-gray-300">
                    <li>Best-practice templates</li>
                    <li>Exportable reports</li>
                    <li>Role-based access</li>
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing CTA */}
      <section id="pricing" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">Simple pricing, generous free tier</h2>
          <p className="mt-3 text-gray-600 dark:text-gray-300">Start free. Upgrade as your team grows—no vendor lock-in.</p>
        </div>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { name: 'Free', price: '$0', items: ['Public demo', 'Email support', 'Community updates'] },
            { name: 'Team', price: '$99/mo', items: ['All analytics', 'Alerts & exports', 'Role-based access'] },
            { name: 'Org', price: 'Custom', items: ['SLA & SSO', 'Custom limits', 'Dedicated support'] },
          ].map((p) => (
            <Card key={p.name}>
              <CardHeader>
                <CardTitle className="text-lg">{p.name}</CardTitle>
                <CardDescription className="text-base">{p.price}</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="mb-6 list-inside list-disc text-sm text-gray-600 dark:text-gray-300">
                  {p.items.map((i) => (<li key={i}>{i}</li>))}
                </ul>
                <Link to={p.name === 'Free' ? '/demo' : '/register'}>
                  <Button className="w-full">{p.name === 'Free' ? 'Explore demo' : 'Get started'}</Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="border-t border-gray-200/70 py-16 dark:border-gray-800">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-center text-3xl font-semibold tracking-tight sm:text-4xl">Frequently asked questions</h2>
          <div className="mt-8 space-y-6">
            {[
              { q: 'Do I need a credit card for the trial?', a: 'No. You can explore the demo and sign up free without a card.' },
              { q: 'Can I invite teammates?', a: 'Yes. Role-based access lets you collaborate securely.' },
              { q: 'Where does the data come from?', a: 'We integrate reputable satellite providers with quality filtering.' },
            ].map((f) => (
              <div key={f.q}>
                <p className="text-base font-medium">{f.q}</p>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{f.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200/70 py-10 dark:border-gray-800">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 text-sm text-gray-600 dark:text-gray-300 sm:flex-row sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-green-600">
              <Satellite className="h-4 w-4 text-white" />
            </div>
            <span className="font-medium">AgriSight</span>
            <span className="text-gray-400">© {new Date().getFullYear()}</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link to="/privacy" className="hover:text-gray-900 dark:hover:text-white">Privacy</Link>
            <Link to="/terms" className="hover:text-gray-900 dark:hover:text-white">Terms</Link>
            <Link to="/support" className="hover:text-gray-900 dark:hover:text-white">Support</Link>
          </nav>
        </div>
      </footer>
    </div>
  );
};

export default Landing;


