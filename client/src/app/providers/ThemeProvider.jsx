import { useEffect, useMemo, useState } from 'react'
import {
	THEME_MODES,
	THEME_STORAGE_KEY,
	ThemeContext,
} from '../../context/ThemeContext.jsx'

function getInitialTheme() {
	if (typeof window === 'undefined') {
		return THEME_MODES.LIGHT
	}

	try {
		const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY)

		if (storedTheme === THEME_MODES.DARK || storedTheme === THEME_MODES.LIGHT) {
			return storedTheme
		}
	} catch {
		return THEME_MODES.LIGHT
	}

	return window.matchMedia('(prefers-color-scheme: dark)').matches
		? THEME_MODES.DARK
		: THEME_MODES.LIGHT
}

export function ThemeProvider({ children }) {
	const [theme, setTheme] = useState(getInitialTheme)

	useEffect(() => {
		const root = document.documentElement

		root.classList.toggle('dark', theme === THEME_MODES.DARK)
		root.style.colorScheme = theme

		try {
			window.localStorage.setItem(THEME_STORAGE_KEY, theme)
		} catch {
			// Ignore storage failures and keep the in-memory theme.
		}
	}, [theme])

	const value = useMemo(
		() => ({
			theme,
			isDark: theme === THEME_MODES.DARK,
			isLight: theme === THEME_MODES.LIGHT,
			setTheme,
			toggleTheme: () => {
				setTheme((currentTheme) =>
					currentTheme === THEME_MODES.DARK ? THEME_MODES.LIGHT : THEME_MODES.DARK,
				)
			},
		}),
		[theme],
	)

	return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}
