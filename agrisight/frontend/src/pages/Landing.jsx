import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Satellite,
  Map,
  BarChart3,
  AlertTriangle,
  ShieldCheck,
  Zap,
  Leaf,
  Globe2,
  Sun,
  Moon,
  Radar,
  Sparkles,
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';

const Landing = () => {
  const [active, setActive] = useState('');
  const [isDark, setIsDark] = useState(false);

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

  useEffect(() => {
    const revealEls = document.querySelectorAll('[data-reveal]');
    if (!revealEls.length) return undefined;

    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('reveal-in');
            revealObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );

    revealEls.forEach((el) => revealObserver.observe(el));
    return () => revealObserver.disconnect();
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem('agrisight-theme');
    const prefersDark =
      window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    const nextIsDark = saved ? saved === 'dark' : prefersDark;
    setIsDark(nextIsDark);
    document.documentElement.classList.toggle('dark', nextIsDark);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
    localStorage.setItem('agrisight-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  useEffect(() => {
    const handleScroll = () => {
      document.documentElement.style.setProperty('--scroll', `${window.scrollY}px`);
    };
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
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
    <div className="min-h-screen bg-white text-gray-900 transition-colors duration-300 dark:bg-slate-950 dark:text-gray-100">
      <style>{`
        .earth-grid {
          background-image:
            radial-gradient(circle at 25% 25%, rgba(56, 189, 248, 0.12), transparent 55%),
            radial-gradient(circle at 75% 35%, rgba(16, 185, 129, 0.12), transparent 55%),
            linear-gradient(rgba(15, 23, 42, 0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(15, 23, 42, 0.06) 1px, transparent 1px);
          background-size: 600px 600px, 700px 700px, 48px 48px, 48px 48px;
          background-position: center, center, center, center;
          transform: translateZ(0);
        }
        .dark .earth-grid {
          background-image:
            radial-gradient(circle at 30% 20%, rgba(56, 189, 248, 0.18), transparent 60%),
            radial-gradient(circle at 70% 40%, rgba(16, 185, 129, 0.18), transparent 60%),
            linear-gradient(rgba(148, 163, 184, 0.16) 1px, transparent 1px),
            linear-gradient(90deg, rgba(148, 163, 184, 0.16) 1px, transparent 1px);
        }
        .parallax-layer {
          transform: translateY(calc(var(--scroll, 0px) * 0.08));
        }
        @keyframes orbit {
          0% { transform: rotate(0deg) translateX(120px) rotate(0deg); }
          100% { transform: rotate(360deg) translateX(120px) rotate(-360deg); }
        }
        .orbit {
          position: absolute;
          top: 18%;
          right: 6%;
          height: 220px;
          width: 220px;
          border-radius: 999px;
          border: 1px dashed rgba(16, 185, 129, 0.25);
        }
        .orbit-marker {
          position: absolute;
          top: 50%;
          left: 50%;
          height: 14px;
          width: 14px;
          margin-top: -7px;
          margin-left: -7px;
          border-radius: 999px;
          background: linear-gradient(135deg, #34d399, #38bdf8);
          box-shadow: 0 0 16px rgba(16, 185, 129, 0.6);
          animation: orbit 12s linear infinite;
        }
        .orbit-marker:nth-child(2) { animation-duration: 16s; animation-delay: -2s; }
        .orbit-marker:nth-child(3) { animation-duration: 20s; animation-delay: -6s; }
        .reveal { opacity: 0; transform: translateY(18px) scale(0.98); transition: opacity 0.6s ease, transform 0.6s ease; }
        .reveal-in { opacity: 1; transform: translateY(0) scale(1); }
      `}</style>
      <div
        className="pointer-events-none absolute inset-0 -z-10 earth-grid parallax-layer"
        aria-hidden="true"
      />
      <header className="sticky top-0 z-30 w-full border-b border-gray-200/70 bg-white/75 backdrop-blur-md dark:border-slate-800 dark:bg-slate-950/80">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500 via-green-500 to-sky-500 shadow-md shadow-emerald-500/30">
              <Satellite className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-semibold tracking-tight">AgriSight</span>
          </div>
          <nav className="hidden gap-6 text-sm md:flex">
            <a
              href="#features"
              onClick={(e) => handleNavClick(e, 'features')}
              className={`${
                active === 'features'
                  ? 'text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-300'
              } hover:text-gray-900 dark:hover:text-white`}
            >
              Capabilities
            </a>
            <a
              href="#use-cases"
              onClick={(e) => handleNavClick(e, 'use-cases')}
              className={`${
                active === 'use-cases'
                  ? 'text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-300'
              } hover:text-gray-900 dark:hover:text-white`}
            >
              Use cases
            </a>
            <a
              href="#pricing"
              onClick={(e) => handleNavClick(e, 'pricing')}
              className={`${
                active === 'pricing'
                  ? 'text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-300'
              } hover:text-gray-900 dark:hover:text-white`}
            >
              Plans
            </a>
            <a
              href="#faq"
              onClick={(e) => handleNavClick(e, 'faq')}
              className={`${
                active === 'faq'
                  ? 'text-gray-900 dark:text-white'
                  : 'text-gray-600 dark:text-gray-300'
              } hover:text-gray-900 dark:hover:text-white`}
            >
              FAQ
            </a>
          </nav>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              className="h-9 w-9 rounded-full"
              onClick={() => setIsDark((prev) => !prev)}
              aria-label="Toggle theme"
            >
              {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Link to="/login">
              <Button variant="ghost">Log in</Button>
            </Link>
            <Link to="/register">
              <Button className="bg-gradient-to-r from-emerald-600 to-sky-500 text-white hover:from-emerald-500 hover:to-sky-400">
                Try it now
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden border-b border-gray-200/70 dark:border-slate-800">
        <div className="pointer-events-none absolute inset-0">
          <div className="orbit">
            <span className="orbit-marker" />
            <span className="orbit-marker" />
            <span className="orbit-marker" />
          </div>
        </div>
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute -left-40 top-10 h-72 w-72 rounded-full bg-emerald-300/30 blur-3xl dark:bg-emerald-500/10" />
          <div className="absolute right-10 top-0 h-80 w-80 rounded-full bg-sky-300/30 blur-3xl dark:bg-sky-500/10" />
          <div className="absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-amber-200/20 blur-3xl dark:bg-amber-500/10" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(15,23,42,0.04),transparent_55%)] dark:bg-[radial-gradient(circle_at_top,rgba(15,23,42,0.35),transparent_55%)]" />
        </div>
        <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-12 px-4 py-16 sm:px-6 lg:grid-cols-2 lg:py-24 lg:px-8">
          <div data-reveal className="reveal">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 shadow-sm shadow-emerald-500/20 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-200">
              <ShieldCheck className="h-3.5 w-3.5" /> Trusted satellite intelligence
            </div>
            <h1 className="mt-4 text-4xl font-semibold tracking-tight sm:text-5xl">
              Monitor crop health, risk, and yield signals from orbit
            </h1>
            <p className="mt-4 max-w-xl text-base text-gray-600 dark:text-gray-300">
              AgriSight turns multi-spectral imagery into clear field-level actions so teams
              can identify stress early, coordinate response, and measure outcomes with
              confidence.
            </p>
            <div className="mt-6 flex flex-wrap items-center gap-3">
              <Link to="/register">
                <Button className="h-11 px-6 bg-gradient-to-r from-emerald-600 to-sky-500 text-white hover:from-emerald-500 hover:to-sky-400">
                  Start monitoring
                </Button>
              </Link>
              <Link to="/demo">
                <Button variant="outline" className="h-11 px-6">View live demo</Button>
              </Link>
            </div>
            <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
              No credit card required. Free trial available.
            </p>
            <div className="mt-8 grid grid-cols-2 gap-4 text-sm text-gray-600 dark:text-gray-300 sm:grid-cols-4">
              <div className="flex items-center gap-2">
                <Leaf className="h-4 w-4 text-emerald-600" /> NDVI, EVI, NDWI
              </div>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500" /> Stress alerts
              </div>
              <div className="flex items-center gap-2">
                <Map className="h-4 w-4 text-sky-500" /> Region tracking
              </div>
              <div className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-indigo-500" /> Analytics
              </div>
            </div>
          </div>
          <div data-reveal className="reveal">
            <div className="relative rounded-2xl border border-emerald-200/60 bg-white/80 p-4 shadow-xl shadow-emerald-500/10 backdrop-blur dark:border-slate-800 dark:bg-slate-900/80">
              <div className="absolute -left-6 -top-6 flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700 shadow-sm dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-200">
                <Radar className="h-3.5 w-3.5" /> Live orbit feed
              </div>
              <div className="aspect-[16/10] w-full overflow-hidden rounded-xl border border-gray-200/70 dark:border-slate-800">
                <img src="/demo/screenshot-2.svg" alt="Platform map screenshot" className="h-full w-full object-cover" />
              </div>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {[
                  { label: 'Scene quality', value: '97%', tone: 'text-emerald-600 dark:text-emerald-300' },
                  { label: 'Last capture', value: '6 min ago', tone: 'text-sky-600 dark:text-sky-300' },
                  { label: 'Active alerts', value: '12', tone: 'text-amber-600 dark:text-amber-300' },
                  { label: 'Regions tracked', value: '146', tone: 'text-indigo-600 dark:text-indigo-300' },
                ].map((stat) => (
                  <div
                    key={stat.label}
                    className="rounded-xl border border-gray-200/70 bg-white/90 p-3 text-sm shadow-sm dark:border-slate-800 dark:bg-slate-900/70"
                  >
                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">{stat.label}</p>
                    <p className={`mt-1 text-lg font-semibold ${stat.tone}`}>{stat.value}</p>
                  </div>
                ))}
              </div>
              <div className="pointer-events-none absolute inset-0 rounded-2xl ring-1 ring-inset ring-black/5 dark:ring-white/5" />
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-700 dark:border-slate-800 dark:bg-slate-900/70 dark:text-slate-200">
            <Sparkles className="h-3.5 w-3.5 text-emerald-500" /> Interactive analytics suite
          </div>
          <h2 className="mt-4 text-3xl font-semibold tracking-tight sm:text-4xl">Everything you need to act early</h2>
          <p className="mt-3 text-gray-600 dark:text-gray-300">
            From ingestion to alerting and reporting, built for field teams and decision makers.
          </p>
        </div>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { icon: Map, title: 'Interactive map', desc: 'Explore regions, draw AOIs, and overlay indices.' },
            { icon: Leaf, title: 'Vegetation indices', desc: 'NDVI, EVI, NDWI, SAVI with trends and anomalies.' },
            { icon: AlertTriangle, title: 'Stress events', desc: 'Detect abnormal patterns and receive notifications.' },
            { icon: BarChart3, title: 'Analytics', desc: 'Dashboards and charts for performance tracking.' },
            { icon: Globe2, title: 'Satellite data', desc: 'Curated, cloud-filtered scenes from trusted providers.' },
            { icon: Zap, title: 'Fast and reliable', desc: 'Optimized pipeline with retries and transparent status.' },
          ].map((f) => (
            <Card
              key={f.title}
              data-reveal
              className="reveal group border border-gray-200/70 bg-white/80 transition-all duration-300 hover:-translate-y-1 hover:border-emerald-200 hover:shadow-lg hover:shadow-emerald-500/10 dark:border-slate-800 dark:bg-slate-900/60 dark:hover:border-emerald-500/40"
            >
              <CardHeader>
                <div className="flex items-start gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-500/10 transition-all duration-300 group-hover:bg-emerald-500/20">
                    <f.icon className="h-5 w-5 text-emerald-700 dark:text-emerald-300" />
                  </div>
                  <div>
                    <CardTitle className="text-base">{f.title}</CardTitle>
                    <CardDescription className="text-sm text-gray-600 dark:text-gray-300">
                      {f.desc}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      <section className="border-t border-b border-gray-200/70 py-12 dark:border-slate-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-center gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <div data-reveal className="reveal group overflow-hidden rounded-xl border border-gray-200/70 bg-white transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-sky-500/10 dark:border-slate-800 dark:bg-slate-900">
              <img src="/demo/screenshot-1.svg" alt="Dashboard screenshot" className="h-full w-full object-cover" />
            </div>
            <div data-reveal className="reveal group overflow-hidden rounded-xl border border-gray-200/70 bg-white transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-500/10 dark:border-slate-800 dark:bg-slate-900">
              <img src="/demo/screenshot-2.svg" alt="Map screenshot" className="h-full w-full object-cover" />
            </div>
            <div data-reveal className="reveal group overflow-hidden rounded-xl border border-gray-200/70 bg-white transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-amber-500/10 dark:border-slate-800 dark:bg-slate-900">
              <img src="/demo/map-preview.svg" alt="Legend and overlays" className="h-full w-full object-cover" />
            </div>
          </div>
        </div>
      </section>

      <section id="use-cases" className="border-t border-b border-gray-200/70 py-16 dark:border-slate-800">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="grid items-start gap-8 lg:grid-cols-3">
            {[
              { title: 'Extension services', desc: 'Target support to farms showing early stress signals.' },
              { title: 'Program M and E', desc: 'Quantify outcomes with consistent, auditable indicators.' },
              { title: 'Risk management', desc: 'Track weather and vegetation anomalies at scale.' },
            ].map((u) => (
              <Card
                key={u.title}
                data-reveal
                className="reveal border border-gray-200/70 bg-white/80 shadow-sm dark:border-slate-800 dark:bg-slate-900/60"
              >
                <CardHeader>
                  <CardTitle className="text-lg">{u.title}</CardTitle>
                  <CardDescription>{u.desc}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                    <p>Best-practice templates</p>
                    <p>Exportable reports</p>
                    <p>Role-based access</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="pricing" className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">Simple pricing, generous free tier</h2>
          <p className="mt-3 text-gray-600 dark:text-gray-300">
            Start free. Upgrade as your team grows with full transparency.
          </p>
        </div>
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[
            { name: 'Free', price: '$0', items: ['Public demo', 'Email support', 'Community updates'] },
            { name: 'Team', price: '$99/mo', items: ['All analytics', 'Alerts and exports', 'Role-based access'] },
            { name: 'Org', price: 'Custom', items: ['SLA and SSO', 'Custom limits', 'Dedicated support'] },
          ].map((p) => (
            <Card
              key={p.name}
              data-reveal
              className="reveal border border-gray-200/70 bg-white/80 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-500/10 dark:border-slate-800 dark:bg-slate-900/60"
            >
              <CardHeader>
                <CardTitle className="text-lg">{p.name}</CardTitle>
                <CardDescription className="text-base">{p.price}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="mb-6 space-y-2 text-sm text-gray-600 dark:text-gray-300">
                  {p.items.map((i) => (
                    <p key={i}>{i}</p>
                  ))}
                </div>
                <Link to={p.name === 'Free' ? '/demo' : '/register'}>
                  <Button className="w-full">{p.name === 'Free' ? 'Explore demo' : 'Get started'}</Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <section id="faq" className="border-t border-gray-200/70 py-16 dark:border-slate-800">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <h2 className="text-center text-3xl font-semibold tracking-tight sm:text-4xl">Frequently asked questions</h2>
          <div className="mt-8 space-y-6">
            {[
              {
                q: 'Do I need a credit card for the trial?',
                a: 'No. You can explore the demo and sign up free without a card.',
              },
              { q: 'Can I invite teammates?', a: 'Yes. Role-based access lets you collaborate securely.' },
              { q: 'Where does the data come from?', a: 'We integrate reputable satellite providers with quality filtering.' },
            ].map((f) => (
              <div
                key={f.q}
                data-reveal
                className="reveal rounded-xl border border-gray-200/70 bg-white/80 p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900/60"
              >
                <p className="text-base font-medium">{f.q}</p>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{f.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t border-gray-200/70 py-10 dark:border-slate-800">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 text-sm text-gray-600 dark:text-gray-300 sm:flex-row sm:px-6 lg:px-8">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-emerald-500 to-sky-500">
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
