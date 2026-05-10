import { redirect } from "next/navigation";

import { createServiceClient } from "@/lib/supabase/server";

async function createRequest(formData: FormData) {
  "use server";

  const supabase = createServiceClient();
  const payload = {
    source: "manual",
    raw_text: null,
    grade: (formData.get("grade") as string) || null,
    length_m: numberOrNull(formData.get("length_m")),
    quantity_t: numberOrNull(formData.get("quantity_t")),
    region: (formData.get("region") as string) || null,
    deadline: (formData.get("deadline") as string) || null,
    condition: numberOrNull(formData.get("condition")),
    extra_conditions: (formData.get("extra_conditions") as string) || null,
    status: "new",
  };
  const { data, error } = await supabase
    .from("requests")
    .insert(payload)
    .select("id")
    .single();
  if (error || !data) throw new Error(error?.message ?? "Не удалось создать заявку");
  redirect(`/requests/${(data as { id: string }).id}`);
}

function numberOrNull(v: FormDataEntryValue | null): number | null {
  if (v === null || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

export default function NewRequestPage() {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Новая заявка</h1>
      <form action={createRequest} className="grid max-w-2xl gap-4">
        <Field name="grade" label="Марка шпунта *" required />
        <Field name="length_m" label="Длина, м" type="number" />
        <Field name="quantity_t" label="Количество, т *" type="number" required />
        <Field name="region" label="Регион доставки *" required />
        <Field name="deadline" label="Срок *" type="date" required />
        <Field name="condition" label="Состояние (1/2/3)" type="number" />
        <label className="grid gap-1">
          <span className="text-sm text-muted-foreground">Доп. условия</span>
          <textarea
            name="extra_conditions"
            rows={3}
            className="rounded-md border border-border bg-background p-2 text-sm"
          />
        </label>
        <button
          type="submit"
          className="mt-2 w-fit rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground"
        >
          Создать
        </button>
        <p className="text-xs text-muted-foreground">
          После создания бот автоматически опубликует пост в группу продавцов.
          (В скелете публикация не выполняется — только запись в БД.)
        </p>
      </form>
    </div>
  );
}

function Field({
  name,
  label,
  type = "text",
  required,
}: {
  name: string;
  label: string;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="grid gap-1">
      <span className="text-sm text-muted-foreground">{label}</span>
      <input
        name={name}
        type={type}
        required={required}
        step={type === "number" ? "any" : undefined}
        className="rounded-md border border-border bg-background p-2 text-sm"
      />
    </label>
  );
}
