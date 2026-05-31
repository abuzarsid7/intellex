import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button, Input } from '@/components/ui'
import { useAuth } from '../context/AuthContext'

export default function Signup() {
	const navigate = useNavigate()
	const { register, isAuthenticated, isLoading, error } = useAuth()
	const [name, setName] = useState('')
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')

	useEffect(() => {
		if (isAuthenticated) {
			navigate('/chat', { replace: true })
		}
	}, [isAuthenticated, navigate])

	const handleSubmit = async (event) => {
		event.preventDefault()
		try {
			await register(name, email, password)
			navigate('/chat')
		} catch {
			// Error state is managed by AuthProvider
		}
	}

	return (
		<main className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(14,165,233,0.18),_transparent_28%),linear-gradient(180deg,_#020617_0%,_#0f172a_100%)] px-6 py-12 text-slate-50">
			<div className="mx-auto grid min-h-[calc(100vh-6rem)] max-w-6xl items-center gap-8 lg:grid-cols-[1.1fr_0.9fr]">
				<section className="space-y-5">
					<p className="text-sm font-semibold uppercase tracking-[0.28em] text-sky-300">Get started</p>
					<h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">Create your Intellex account.</h1>
					<p className="max-w-xl text-lg leading-8 text-slate-300">
						Register once and your conversations will persist across sessions.
					</p>
					<Link to="/login" className="inline-flex text-sm text-sky-300 underline-offset-4 hover:underline">
						Already have an account? Sign in.
					</Link>
				</section>

				<section className="rounded-[2rem] border border-white/10 bg-white/5 p-6 shadow-2xl shadow-slate-950/40 backdrop-blur sm:p-8">
					<form onSubmit={handleSubmit} className="space-y-4">
						<Input
							label="Name"
							type="text"
							value={name}
							onChange={(event) => setName(event.target.value)}
							placeholder="Your name"
							required
						/>
						<Input
							label="Email"
							type="email"
							value={email}
							onChange={(event) => setEmail(event.target.value)}
							placeholder="you@example.com"
							required
						/>
						<Input
							label="Password"
							type="password"
							value={password}
							onChange={(event) => setPassword(event.target.value)}
							placeholder="At least 6 characters"
							required
						/>

						{error && <p className="text-sm text-red-300">{error}</p>}

						<Button type="submit" variant="primary" size="lg" disabled={isLoading} className="w-full rounded-full">
							{isLoading ? 'Creating account...' : 'Create account'}
						</Button>
					</form>
				</section>
			</div>
		</main>
	)
}
