"use client";

import { useRouter } from "next/navigation";

import { createClient } from "@/lib/supabase/client";

export function SignOutButton({ email }: { email: string }) {
  const router = useRouter();
  const supabase = createClient();

  async function onClick() {
    await supabase.auth.signOut();
    router.replace("/login");
    router.refresh();
  }

  return (
    <button
      onClick={onClick}
      className="text-muted-foreground hover:text-foreground"
      title={`Выйти (${email})`}
    >
      Выйти
    </button>
  );
}
