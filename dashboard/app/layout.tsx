import type { Metadata } from "next";
import Link from "next/link";

import { SignOutButton } from "@/components/SignOutButton";
import { createClient } from "@/lib/supabase/server";
import "./globals.css";

export const metadata: Metadata = {
  title: "АЗИМУТ — Закупка шпунта",
  description: "Дашборд автоматизации закупки б/у шпунта",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  return (
    <html lang="ru">
      <body>
        <header className="border-b border-border">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <Link href="/" className="text-lg font-semibold">
              АЗИМУТ · Закупка шпунта
            </Link>
            <nav className="flex items-center gap-6 text-sm text-muted-foreground">
              {user ? (
                <>
                  <Link href="/" className="hover:text-foreground">Заявки</Link>
                  <Link href="/requests/new" className="hover:text-foreground">Новая</Link>
                  <Link href="/settings" className="hover:text-foreground">Настройки</Link>
                  <SignOutButton email={user.email ?? ""} />
                </>
              ) : (
                <Link href="/login" className="hover:text-foreground">Войти</Link>
              )}
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
