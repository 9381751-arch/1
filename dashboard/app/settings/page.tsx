import { revalidatePath } from "next/cache";

import { createClient, createServiceClient } from "@/lib/supabase/server";
import { SettingRow } from "@/lib/types";

export const dynamic = "force-dynamic";

async function updateSettings(formData: FormData) {
  "use server";

  const supabase = createServiceClient();
  const updates: { key: string; value: string }[] = [];
  for (const [key, value] of formData.entries()) {
    if (typeof value === "string") {
      updates.push({ key, value });
    }
  }
  for (const u of updates) {
    await supabase
      .from("settings")
      .upsert({ key: u.key, value: u.value, updated_at: new Date().toISOString() });
  }
  revalidatePath("/settings");
}

export default async function SettingsPage() {
  const supabase = createClient();
  const { data } = await supabase
    .from("settings")
    .select("*")
    .order("key");
  const rows = (data ?? []) as SettingRow[];

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Настройки</h1>
      <form action={updateSettings} className="grid max-w-3xl gap-4">
        {rows.map((s) => (
          <label key={s.key} className="grid gap-1">
            <span className="text-sm font-medium">{s.key}</span>
            {s.description && (
              <span className="text-xs text-muted-foreground">{s.description}</span>
            )}
            <input
              name={s.key}
              defaultValue={s.value ?? ""}
              className="rounded-md border border-border bg-background p-2 text-sm"
            />
          </label>
        ))}
        {rows.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Настройки ещё не загружены — примените миграции и seed.
          </p>
        )}
        <button
          type="submit"
          className="mt-2 w-fit rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
        >
          Сохранить
        </button>
      </form>
    </div>
  );
}
