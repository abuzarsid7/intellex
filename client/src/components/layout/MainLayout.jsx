import Sidebar from './Sidebar'
import Navbar from './Navbar'

export default function MainLayout({ children, sidebarProps }) {
	return (
		<div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgb(var(--app-accent)/0.14),_transparent_35%),linear-gradient(180deg,_rgb(var(--app-background))_0%,_rgb(var(--app-surface))_100%)] text-[rgb(var(--app-foreground))] transition-colors duration-300">
			<Navbar />
			<div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl gap-4 px-4 py-4 lg:px-6">
				<Sidebar {...sidebarProps} />
				<main className="min-w-0 flex-1 overflow-hidden rounded-3xl border border-[rgb(var(--app-border))] bg-[rgb(var(--app-surface))]/85 shadow-2xl shadow-slate-950/20 backdrop-blur transition-colors duration-300">
					{children}
				</main>
			</div>
		</div>
	)
}
