import { notFound } from "next/navigation";

import { createClient } from "@/lib/supabase/server";
import { OfferRow, RequestRow, STATUS_LABEL } from "@/lib/types";
import { formatDate, formatNumber } from "@/lib/utils";

export const dynamic = "force-dynamic";

export default async function RequestDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const supabase = createClient();

  const { data: request } = await supabase
    .from("requests")
    .select("*")
    .eq("id", params.id)
    .single();

  if (!request) notFound();

  const { data: offers } = await supabase
    .from("offers")
    .select("*")
    .eq("request_id", params.id)
    .order("total_cost_per_t", { ascending: true, nullsFirst: false });

  const r = request as RequestRow;
  const offerRows = (offers ?? []) as OfferRow[];

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-semibold">
          Заявка <span className="font-mono text-base">#{r.id.slice(0, 8)}</span>
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Статус: <span className="font-medium text-foreground">{STATUS_LABEL[r.status]}</span>
          {" · "}создана {formatDate(r.created_at)}
        </p>
      </header>

      <section className="grid gap-4 rounded-lg border border-border p-4 sm:grid-cols-2 md:grid-cols-3">
        <Field label="Марка" value={r.grade} />
        <Field label="Длина, м" value={r.length_m ? formatNumber(r.length_m) : null} />
        <Field label="Количество, т" value={r.quantity_t ? formatNumber(r.quantity_t) : null} />
        <Field label="Регион" value={r.region} />
        <Field label="Срок" value={formatDate(r.deadline)} />
        <Field label="Состояние" value={r.condition?.toString() ?? null} />
        {r.extra_conditions && (
          <div className="sm:col-span-2 md:col-span-3">
            <Field label="Доп. условия" value={r.extra_conditions} />
          </div>
        )}
      </section>

      {r.claude_post_text && (
        <section>
          <h2 className="mb-2 text-lg font-semibold">Пост в группе продавцов</h2>
          <pre className="whitespace-pre-wrap rounded-lg border border-border bg-muted p-4 text-sm">
{r.claude_post_text}
          </pre>
        </section>
      )}

      <section>
        <h2 className="mb-3 text-lg font-semibold">Предложения ({offerRows.length})</h2>
        <div className="overflow-hidden rounded-lg border border-border">
          <table className="w-full text-sm">
            <thead className="bg-muted text-muted-foreground">
              <tr>
                <th className="px-3 py-2 text-left">#</th>
                <th className="px-3 py-2 text-left">Продавец</th>
                <th className="px-3 py-2 text-right">Цена/т</th>
                <th className="px-3 py-2 text-right">Лог./т</th>
                <th className="px-3 py-2 text-right">Себес/т</th>
                <th className="px-3 py-2 text-right">Кол-во, т</th>
                <th className="px-3 py-2 text-left">Город</th>
                <th className="px-3 py-2 text-left">Торг</th>
              </tr>
            </thead>
            <tbody>
              {offerRows.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-3 py-8 text-center text-muted-foreground">
                    Предложений пока нет
                  </td>
                </tr>
              )}
              {offerRows.map((o) => (
                <tr key={o.id} className="border-t border-border">
                  <td className="px-3 py-2">{o.rank ?? "—"}</td>
                  <td className="px-3 py-2">
                    {o.seller_name ?? o.seller_username ?? `#${o.seller_tg_id}`}
                  </td>
                  <td className="px-3 py-2 text-right">{formatNumber(o.price_per_t)}</td>
                  <td className="px-3 py-2 text-right">{formatNumber(o.logistics_per_t)}</td>
                  <td className="px-3 py-2 text-right font-medium">
                    {formatNumber(o.total_cost_per_t)}
                  </td>
                  <td className="px-3 py-2 text-right">{formatNumber(o.quantity_t)}</td>
                  <td className="px-3 py-2">{o.location ?? "—"}</td>
                  <td className="px-3 py-2">{o.negotiation_status ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string | null | undefined }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className="mt-0.5 text-sm">{value ?? "—"}</div>
    </div>
  );
}
