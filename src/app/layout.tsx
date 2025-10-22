import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import '../styles/globals.css';
import { UserProvider } from './contexts/UserContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Konnect - Campus Economy Hub',
  description: 'Buy, sell, and manage your campus economy with Konnect',
  manifest: '/manifest.json',
  themeColor: '#9945FF',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'Konnect',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <UserProvider>{children}</UserProvider>
      </body>
    </html>
  );
}
