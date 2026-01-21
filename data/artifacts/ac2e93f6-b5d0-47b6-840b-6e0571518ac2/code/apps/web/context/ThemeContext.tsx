'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Define the shape of the theme object
interface Theme {
    primary: string;
    secondary: string;
    surface: string;
    text: string;
    background: string;
    [key: string]: string;
}

// Define the context props
interface ThemeContextType {
    theme: Theme;
    setTheme: (theme: Theme) => void;
}

// Default theme values
const defaultTheme: Theme = {
    primary: '#3498db',
    secondary: '#9b59b7',
    surface: '#ffffff',
    text: '#333333',
    background: '#f4f4f4',
};

// Create the context
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

// Provider component
export function ThemeProvider({ children }: { children: ReactNode }) {
    const [theme, setTheme] = useState<Theme>(defaultTheme);

    useEffect(() => {
        // Load theme from local storage on mount
        const storedTheme = localStorage.getItem('theme');
        if (storedTheme) {
            try {
                setTheme(JSON.parse(storedTheme));
            } catch (error) {
                console.error('Failed to parse stored theme:', error);
            }
        }
    }, []);

    const updateTheme = (newTheme: Theme) => {
        setTheme(newTheme);
        localStorage.setItem('theme', JSON.stringify(newTheme));
    };

    return (
        <ThemeContext.Provider value={{ theme, setTheme: updateTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

// Hook to use the theme context
export function useTheme() {
    const context = useContext(ThemeContext);
    if (context === undefined) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
}
