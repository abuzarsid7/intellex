import { createContext, useContext } from 'react'
export const THEME_STORAGE_KEY = 'intellex-theme'
export const THEME_MODES = {
	LIGHT: 'light',
	DARK: 'dark',
}

export const ThemeContext = createContext(undefined)

export function useTheme() {
	const context = useContext(ThemeContext)

	if (!context) {
		throw new Error('useTheme must be used within a ThemeProvider')
	}

	return context
}
