import Link from "next/link";

import { createClient } from "@/lib/supabase/server";
import { RequestRow, STATUS_LABEL } from "@/lib/types";
import { formatDate, formatNumber } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function RequestsListPage() {
  const supabase = createClient();
  const { data, error } = await supabase
    .from("requests")
    .select("*")
    .order("created_at", { ascending: false })
    .limit(100);

  const rows = (data ?? []) as RequestRow[];

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Заявки</h1>
        <Link
          href="/requests/new"
          className="rounded-md bg-primary px-3 py-2 text-sm text-primary-foreground hover:opacity-90"
        >
          Новая заявка
        </Link>
      </div>

      {error && (
        <div className="mb-4 rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-900">
          Ошибка загрузки: {error.message}
        </div>
      )}

      <div className="overflow-hidden rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="bg-muted text-muted-foreground">
            <tr>
              <th className="px-3 py-2 text-left">Дата</th>
              <th className="px-3 py-2 text-left">Марка</th>
              <th className="px-3 py-2 text-right">Кол-во, т</th>
              <th className="px-3 py-2 text-left">Регион</th>
              <th className="px-3 py-2 text-left">Срок</th>
              <th className="px-3 py-2 text-left">Статус</th>
              <th className="px-3 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 && (
              <tr>
                <td colSpan={7} className="px-3 py-8 text-center text-muted-foreground">
                  Заявок пока нет
                </td>
              </tr>
            )}
            {rows.map((r) => (
              <tr key={r.id} className="border-t border-border hover:bg-muted/50">
                <td className="px-3 py-2">{formatDate(r.created_at)}</td>
                <td className="px-3 py-2">{r.grade ?? "—"}</td>
                <td className="px-3 py-2 text-right">{formatNumber(r.quantity_t)}</td>
                <td className="px-3 py-2">{r.region ?? "—"}</td>
                <td className="px-3 py-2">{formatDate(r.deadline)}</td>
                <td className="px-3 py-2">{STATUS_LABEL[r.status] ?? r.status}</td>
                <td className="px-3 py-2 text-right">
                  <Link href={`/requests/${r.id}`} className="text-primary underline">
                    открыть
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
