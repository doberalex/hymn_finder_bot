import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Гимны — поддержка приложения',
  description: 'Помощь, контакты и политика конфиденциальности приложения «Гимны».',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ru"><body>{children}</body></html>;
}
