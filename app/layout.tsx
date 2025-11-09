import './globals.css'
import { Inter } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import { AnalysisProvider } from '@/contexts/AnalysisContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'PulseCompass - Advanced Stock Analysis',
  description: 'AI-powered equity analysis with legendary investor perspectives',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <AnalysisProvider>
          <div className="min-h-screen bg-neutral-50 dark:bg-dark-bg transition-colors duration-200">
            {children}
          </div>
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </AnalysisProvider>
      </body>
    </html>
  )
}
