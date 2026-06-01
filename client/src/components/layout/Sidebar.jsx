import { useEffect, useRef, useState } from 'react'
import { Button, ChatListSkeleton, Input } from '@/components/ui'

export default function Sidebar({
	chats = [],
	currentChat,
	onNewChat,
	onSelectChat,
	onEditChat,
	onDeleteChat,
	isLoading = false,
	isFetchingChats = false,
}) {
	const [editingChatId, setEditingChatId] = useState(null)
	const [draftTitle, setDraftTitle] = useState('')
	const draftInputRef = useRef(null)

	useEffect(() => {
		if (editingChatId) {
			draftInputRef.current?.focus()
			draftInputRef.current?.select()
		}
	}, [editingChatId])

	const beginEdit = (chat) => {
		setEditingChatId(chat._id)
		setDraftTitle(chat.title || 'New Chat')
	}

	const cancelEdit = () => {
		setEditingChatId(null)
		setDraftTitle('')
	}

	const saveEdit = async (chat) => {
		const nextTitle = draftTitle.trim()
		if (!nextTitle) {
			cancelEdit()
			return
		}

		if (nextTitle !== (chat.title || 'New Chat')) {
			await onEditChat?.(chat._id, nextTitle)
		}

		cancelEdit()
	}

	return (
		<aside className="hidden w-80 shrink-0 flex-col rounded-3xl border border-[rgb(var(--app-border))] bg-[rgb(var(--app-surface))]/85 p-4 text-[rgb(var(--app-foreground))] shadow-2xl shadow-slate-950/20 backdrop-blur transition-colors duration-300 lg:flex">
			<div className="mb-4 flex items-center justify-between gap-3">
				<div>
					<p className="text-sm font-semibold uppercase tracking-[0.24em] text-[rgb(var(--app-foreground))]">Chats</p>
					<p className="text-xs text-[rgb(var(--app-muted))]">Your saved conversations</p>
				</div>
				<Button
					variant="primary"
					size="sm"
					onClick={onNewChat}
					disabled={isLoading || isFetchingChats}
					className="rounded-full px-4"
				>
					New chat
				</Button>
			</div>

			<div className="flex-1 space-y-2 overflow-y-auto pr-1">
				{isFetchingChats ? (
					<ChatListSkeleton />
				) : chats.length === 0 ? (
					<div className="rounded-2xl border border-dashed border-[rgb(var(--app-border))] bg-[rgb(var(--app-background))]/50 p-6 text-center transition-colors duration-300">
						<div className="mb-2 text-3xl">💭</div>
						<p className="text-sm font-medium text-[rgb(var(--app-foreground))]">No chats yet</p>
						<p className="mt-1 text-xs text-[rgb(var(--app-muted))]">Create a new chat to get started</p>
					</div>
				) : (
					chats.map((chat) => {
						const isActive = currentChat?._id === chat._id

						return (
							<div
								key={chat._id}
								className={`rounded-2xl border px-4 py-3 text-left transition-colors duration-300 ${
									isActive
										? 'border-sky-400/40 bg-[rgb(var(--app-accent))]/10 text-[rgb(var(--app-foreground))]'
										: 'border-[rgb(var(--app-border))] bg-[rgb(var(--app-background))]/50 text-[rgb(var(--app-foreground))] hover:bg-[rgb(var(--app-background))]/80'
								}`}
							>
								<div className="flex items-start justify-between gap-3">
									<div className="min-w-0 flex-1">
										{editingChatId === chat._id ? (
											<Input
												ref={draftInputRef}
												value={draftTitle}
												onChange={(event) => setDraftTitle(event.target.value)}
												onBlur={() => saveEdit(chat)}
												onKeyDown={(event) => {
													if (event.key === 'Enter') {
														event.preventDefault()
														saveEdit(chat)
													}
													if (event.key === 'Escape') {
														event.preventDefault()
														cancelEdit()
													}
												}}
												className="w-full"
											/>
										) : (
											<button
												type="button"
												onClick={() => onSelectChat?.(chat._id)}
												className="w-full text-left"
											>
												<p className="truncate text-sm font-medium">{chat.title || 'New Chat'}</p>
											</button>
										)}
									</div>
									<span className="rounded-full bg-[rgb(var(--app-background))]/70 px-2 py-0.5 text-[10px] uppercase tracking-[0.24em] text-[rgb(var(--app-muted))]">
										{isActive ? 'Open' : 'Saved'}
									</span>
								</div>

								<div className="mt-3 flex items-center gap-3">
								{onEditChat && editingChatId !== chat._id && (
									<button
										type="button"
										onClick={(event) => {
											event.stopPropagation()
											beginEdit(chat)
										}}
										className="inline-flex text-xs text-[rgb(var(--app-muted))] hover:text-[rgb(var(--app-foreground))]"
									>
										Edit name
									</button>
								)}
								{onDeleteChat && (
									<button
										type="button"
										onClick={(event) => {
											event.stopPropagation()
											const shouldDelete = window.confirm('Delete this chat permanently?')
											if (shouldDelete) {
												onDeleteChat(chat._id)
											}
										}}
										className="mt-3 inline-flex text-xs text-[rgb(var(--app-muted))] hover:text-red-500"
									>
										Delete chat
									</button>
								)}
								</div>
							</div>
						)
					})
				)}
			</div>
		</aside>
	)
}

