import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
    title: 'Idea-to-Deploy Platform',
    description: 'AI-Powered SaaS Factory',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className="dark">
            <body className="min-h-screen bg-background font-sans antialiased text-foreground selection:bg-primary selection:text-primary-foreground">
                {children}
            </body>
        </html>
    )
}
