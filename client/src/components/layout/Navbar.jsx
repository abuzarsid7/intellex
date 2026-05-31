import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui'
import { useAuth } from '../../context/AuthContext'
import { useTheme } from '../../hooks/useTheme'

function ThemeIcon({ isDark }) {
	return isDark ? (
		<svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
			<path
				d="M21.64 13.65A9 9 0 1 1 10.35 2.36a1 1 0 0 1 1.24 1.24A7 7 0 1 0 20.4 12.41a1 1 0 0 1 1.24 1.24Z"
			/>
		</svg>
	) : (
		<svg viewBox="0 0 24 24" aria-hidden="true" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
			<circle cx="12" cy="12" r="4" />
			<path d="M12 2v2" />
			<path d="M12 20v2" />
			<path d="m4.93 4.93 1.41 1.41" />
			<path d="m17.66 17.66 1.41 1.41" />
			<path d="M2 12h2" />
			<path d="M20 12h2" />
			<path d="m6.34 17.66-1.41 1.41" />
			<path d="m19.07 4.93-1.41 1.41" />
		</svg>
	)
}

export default function Navbar() {
	const { isAuthenticated, user, logout } = useAuth()
	const { theme, toggleTheme } = useTheme()
	const navigate = useNavigate()

	const handleLogout = async () => {
		await logout()
		navigate('/login')
	}

	return (
		<header className="sticky top-0 z-30 border-b border-[rgb(var(--app-border))] bg-[rgb(var(--app-surface))]/90 backdrop-blur">
			<div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 lg:px-6">
				<Link to="/" className="flex items-center gap-3">
					<div className="grid h-9 w-9 place-items-center rounded-2xl bg-sky-500/15 text-sky-600 ring-1 ring-inset ring-sky-400/30 dark:text-sky-300">
						I
					</div>
					<div>
						<p className="text-sm font-semibold uppercase tracking-[0.22em] text-sky-700 dark:text-sky-300">Intellex</p>
						<p className="text-xs text-[rgb(var(--app-muted))]">Persistent AI chat</p>
					</div>
				</Link>

				<div className="flex items-center gap-2">
					<Button
						variant="ghost"
						size="sm"
						onClick={toggleTheme}
						aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
						className="h-10 w-10 rounded-full border border-[rgb(var(--app-border))] bg-[rgb(var(--app-surface))] p-0 text-[rgb(var(--app-foreground))] hover:bg-slate-100 dark:bg-white/5 dark:text-slate-100 dark:hover:bg-white/10"
					>
						<ThemeIcon isDark={theme === 'dark'} />
					</Button>

					{isAuthenticated ? (
						<>
							<div className="hidden items-center gap-2 rounded-full border border-[rgb(var(--app-border))] bg-[rgb(var(--app-surface))] px-3 py-1.5 text-sm text-[rgb(var(--app-foreground))] sm:flex">
								<span className="h-2 w-2 rounded-full bg-emerald-400" />
								{user?.name || user?.email || 'Signed in'}
							</div>
							<Button variant="secondary" size="sm" onClick={handleLogout} className="rounded-full border border-[rgb(var(--app-border))] bg-[rgb(var(--app-surface))] px-4 text-[rgb(var(--app-foreground))] hover:bg-slate-50 dark:bg-white/90 dark:text-slate-950 dark:hover:bg-white">
								Logout
							</Button>
						</>
					) : (
						<div className="flex items-center gap-2">
							<Button variant="ghost" size="sm" onClick={() => navigate('/login')} className="rounded-full border border-[rgb(var(--app-border))] px-4 text-[rgb(var(--app-foreground))] hover:bg-slate-100 dark:text-slate-100 dark:hover:bg-white/10">
								Login
							</Button>
							<Button variant="primary" size="sm" onClick={() => navigate('/signup')} className="rounded-full px-4">
								Sign up
							</Button>
						</div>
					)}
				</div>
			</div>
		</header>
	)
}
