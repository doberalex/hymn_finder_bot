import time
import uuid
import re

from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)

from app.services.search_service import (
    search_hymns,
    highlight_text,
    build_preview
)

from app.services.log_service import log_search


# 📖 INLINE РЕЖИМ
async def inline_search(inline_query: InlineQuery):
    query = inline_query.query.strip()

    if len(query) > 300:
        await inline_query.answer([], cache_time=5, is_personal=True)
        return
    start_time = time.time()

    # если пусто — показываем дефолтные песни
    if not query:
        results = await search_hymns("", limit=5)
    else:
        results = await search_hymns(query, limit=20)

    response_time = round(time.time() - start_time, 2)

    # логируем только полезные запросы
    query_for_log = query.strip()

    should_log = False

    if query_for_log.isdigit():
        # номера песен: 11, 111, 1123
        should_log = len(query_for_log) >= 2
    else:
        # обычный текст
        should_log = len(query_for_log) >= 3

    if should_log:
        await log_search(
            inline_query.from_user,
            query,
            None,
            len(results),
            "inline",
            response_time
        )

    articles = []

    for row in results:
        preview_raw = build_preview(
            row['content'],
            query,
            radius=40
        )

        # удаляем "Куплет", "Куплет 1", и т.д.
        preview_raw = re.sub(
            r"\bкуплет\s*\d*\b[:.]?",
            "",
            preview_raw,
            flags=re.IGNORECASE
        )

        # убираем лишние пробелы
        preview_raw = re.sub(
            r"\s{2,}",
            " ",
            preview_raw
        ).strip()

        full_text = highlight_text(
            row['content'],
            query
        )

        if row.get("tune"):
            tune_text = f"\n🎼 Тональность: {row['tune']}\n\n"
        else:
            tune_text = "\n\n"

        text = (
            f"🎵 <b>{row['number']}. "
            f"{highlight_text(row['title'], query)}</b>\n"
            f"📂 {row['songbook'] or 'Без сборника'}"
            f"{tune_text}"
            f"{full_text}"
        )

        articles.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=(
                    f"🎵{row['number']}. "
                    f"{row['title']}, "
                    f"📂 {row['songbook'] or 'Без сборника'}"
                ),
                description=preview_raw,
                thumb_url="https://s22nrg.storage.yandex.net/rdisk/c423f035a0a8ac79460d016a2d287747bca0f7d349dff306da3e2f8ca1eb1fa5/69f9ea3a/xnY3PcRIp8nklvOwbqlEH1UkPQ_MnoFytnF1nb953hMjR2Vq4b3PIixNA2ngMzYcDwZ20DcM4uO_UcUMWxGenA==?uid=0&filename=logo.png&disposition=inline&hash=&limit=0&content_type=image%2Fpng&owner_uid=0&fsize=398217&hid=98aef8ee6814e31438a4ff6196b6bb8c&media_type=image&tknv=v3&etag=08481c76b5417ab9985f60df22b6dad7&ts=65111a6438280&s=4e944e0d083c0514a09f601e1062bdd11e4f9f3bf58da2264133e60d5fea3dcf&pb=U2FsdGVkX1-Pkig4JvT08fWBp5bFZnLI6ZO3j2Bd2o3qhkVkU_WWi11mKHmOVk1KS_NcNqO7mSFIip7x5aDRwS8hRwzAKVsMYzeQrUiduH8",
                input_message_content=InputTextMessageContent(
                    message_text=text,
                    parse_mode="HTML"
                )
            )
        )

    await inline_query.answer(
        articles,
        cache_time=1
    )
