import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "АЗИМУТ — Закупка шпунта",
  description: "Дашборд автоматизации закупки б/у шпунта",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body>
        <header className="border-b border-border">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <Link href="/" className="text-lg font-semibold">
              АЗИМУТ · Закупка шпунта
            </Link>
            <nav className="flex gap-6 text-sm text-muted-foreground">
              <Link href="/" className="hover:text-foreground">Заявки</Link>
              <Link href="/requests/new" className="hover:text-foreground">Новая</Link>
              <Link href="/settings" className="hover:text-foreground">Настройки</Link>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
