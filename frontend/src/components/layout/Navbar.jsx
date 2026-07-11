import { Link, useLocation } from 'react-router-dom'
import { Activity, MessageCircle, Stethoscope } from 'lucide-react'

export default function Navbar() {
  const { pathname } = useLocation()

  const links = [
    { to: '/', label: 'Home' },
    { to: '/assess', label: 'Assessment' },
    { to: '/chat', label: 'Chat' },
  ]

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-strong">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/30
                          flex items-center justify-center group-hover:bg-emerald-500/30 transition-colors">
            <Activity size={16} className="text-emerald-400" />
          </div>
          <span className="font-display font-semibold text-lg text-slate-100">
            Arogya <span className="text-emerald-400">AI</span>
          </span>
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {links.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                ${pathname === to
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                }`}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* CTA */}
        <Link to="/assess" className="btn-primary text-sm py-2 px-4 hidden sm:flex items-center gap-2">
          <Stethoscope size={15} />
          Start Assessment
        </Link>
      </div>
    </nav>
  )
}
