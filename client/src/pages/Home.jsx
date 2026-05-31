import { Link } from 'react-router-dom'
import { Button } from '@/components/ui'

export default function Home() {
	return (
		<main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(14,165,233,0.25),_transparent_30%),radial-gradient(circle_at_80%_20%,_rgba(16,185,129,0.16),_transparent_26%),linear-gradient(180deg,_#020617_0%,_#0f172a_100%)] text-slate-50">
			<section className="mx-auto flex min-h-screen max-w-7xl items-center px-6 py-12 lg:px-8">
				<div className="grid w-full gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
					<div className="max-w-2xl">
						<p className="inline-flex rounded-full border border-sky-400/30 bg-sky-500/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.28em] text-sky-300">
							Intellex workspace
						</p>
						<h1 className="mt-6 text-5xl font-semibold tracking-tight sm:text-6xl lg:text-7xl">
							A chat system that stores, retrieves, and reasons over your documents.
						</h1>
						<p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
							Sign in, upload PDFs, and ask questions grounded in your own vector store. The conversation stays in sync with MongoDB, while document context comes from Chroma-powered retrieval.
						</p>

						<div className="mt-8 flex flex-wrap gap-3">
							<Button as={Link} to="/signup" variant="primary" size="lg" className="rounded-full px-6">
								Get started
							</Button>
							<Button as={Link} to="/login" variant="secondary" size="lg" className="rounded-full border border-white/10 bg-white/90 px-6 text-slate-950 hover:bg-white">
								Sign in
							</Button>
							<Button as={Link} to="/chat" variant="ghost" size="lg" className="rounded-full border border-white/10 px-6 text-slate-100 hover:bg-white/10">
								Open chat
							</Button>
						</div>

						<div className="mt-10 grid gap-4 sm:grid-cols-3">
							<div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
								<p className="text-sm text-slate-400">Chats</p>
								<p className="mt-2 text-2xl font-semibold">Persistent</p>
							</div>
							<div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
								<p className="text-sm text-slate-400">Upload</p>
								<p className="mt-2 text-2xl font-semibold">PDF RAG</p>
							</div>
							<div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
								<p className="text-sm text-slate-400">Retrieval</p>
								<p className="mt-2 text-2xl font-semibold">Chroma</p>
							</div>
						</div>
					</div>

					<div className="rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-2xl shadow-slate-950/40 backdrop-blur">
						<div className="rounded-3xl border border-white/10 bg-slate-950/70 p-5">
							<p className="text-sm uppercase tracking-[0.24em] text-slate-400">What happens next</p>
							<div className="mt-5 space-y-3 text-sm text-slate-200">
								<div className="rounded-2xl bg-white/5 px-4 py-3">1. Log in or create an account</div>
								<div className="rounded-2xl bg-sky-500/10 px-4 py-3 text-sky-200">2. Upload a PDF to index it in Chroma</div>
								<div className="rounded-2xl bg-emerald-500/10 px-4 py-3 text-emerald-200">3. Ask questions grounded in the uploaded content</div>
								<div className="rounded-2xl bg-amber-500/10 px-4 py-3 text-amber-200">4. Keep the chat history persisted in MongoDB</div>
							</div>
						</div>
					</div>
				</div>
			</section>
		</main>
	)
}
