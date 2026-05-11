-- Дефолтные значения настроек. Конкретные числа уточнит заказчик
-- (см. п.10 ТЗ — тарифная сетка, агрессивность торга).

insert into public.settings (key, value, description) values
    ('logistics_rate_per_t_km',  '12',   'Базовый тариф логистики, руб/т·км'),
    ('logistics_min_per_t',      '500',  'Минимальная ставка логистики, руб/т'),
    ('negotiation_top_n',        '3',    'Сколько ТОП-продавцов получают контрпредложение'),
    ('negotiation_discount_pct', '5',    'Скидка от лучшей цены в контрпредложении, %'),
    ('collect_deadline_hours',   '4',    'Время сбора предложений до запуска торга, часов'),
    ('negotiation_deadline_hours','2',   'Время на ответ в торговом раунде, часов'),
    ('tg_group_sellers_id',      '',     'ID Telegram-группы продавцов'),
    ('tg_channel_requests_id',   '',     'ID Telegram-канала заявок'),
    ('tg_manager_id',            '',     'ID менеджера (личка для итоговых отчётов)')
on conflict (key) do nothing;
