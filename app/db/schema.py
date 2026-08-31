import aiomysql


async def _column_exists(cursor, table: str, column: str) -> bool:
    await cursor.execute(
        """SELECT 1 FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND COLUMN_NAME=%s LIMIT 1""",
        (table, column),
    )
    return await cursor.fetchone() is not None


async def _index_exists(cursor, table: str, index: str) -> bool:
    await cursor.execute(
        """SELECT 1 FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s AND INDEX_NAME=%s LIMIT 1""",
        (table, index),
    )
    return await cursor.fetchone() is not None


async def _add_column(cursor, table: str, column: str, definition: str) -> None:
    if not await _column_exists(cursor, table, column):
        await cursor.execute(f"ALTER TABLE `{table}` ADD COLUMN `{column}` {definition}")


async def apply_schema(pool) -> None:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS songbooks (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    normalized_title VARCHAR(255) NOT NULL DEFAULT '',
                    search_key VARCHAR(255) NOT NULL,
                    language_code VARCHAR(8) NULL,
                    source_slug VARCHAR(191) NULL,
                    display_order INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_songbooks_search_key (search_key)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"""
            )
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS hymns (
                    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(500) NOT NULL,
                    content LONGTEXT NOT NULL,
                    songbook_id INT UNSIGNED NOT NULL,
                    number INT NOT NULL DEFAULT 0,
                    tune VARCHAR(500) NOT NULL DEFAULT '',
                    words VARCHAR(500) NOT NULL DEFAULT '',
                    source_key VARCHAR(191) NULL,
                    search_key VARCHAR(1000) NOT NULL,
                    title_normalized VARCHAR(500) NOT NULL DEFAULT '',
                    content_normalized LONGTEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    KEY idx_hymns_songbook_number (songbook_id, number),
                    UNIQUE KEY uq_hymns_search_key (search_key(191))
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"""
            )
            await _add_column(cursor, "songbooks", "language_code", "VARCHAR(8) NULL")
            await _add_column(cursor, "songbooks", "source_slug", "VARCHAR(191) NULL")
            await _add_column(cursor, "songbooks", "display_order", "INT NOT NULL DEFAULT 0")
            await _add_column(cursor, "hymns", "words", "VARCHAR(500) NOT NULL DEFAULT ''")
            await _add_column(cursor, "hymns", "source_key", "VARCHAR(191) NULL")
            if not await _index_exists(cursor, "songbooks", "uq_songbooks_source"):
                await cursor.execute("CREATE UNIQUE INDEX uq_songbooks_source ON songbooks (language_code, source_slug)")
            if not await _index_exists(cursor, "hymns", "uq_hymns_source_key"):
                await cursor.execute("CREATE UNIQUE INDEX uq_hymns_source_key ON hymns (source_key)")
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS bot_users (
                    user_id BIGINT NOT NULL PRIMARY KEY,
                    interface_language VARCHAR(8) NOT NULL DEFAULT 'ru',
                    catalog_language VARCHAR(8) NULL,
                    search_scope VARCHAR(16) NOT NULL DEFAULT 'all',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"""
            )
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS user_favorites (
                    user_id BIGINT NOT NULL, hymn_id BIGINT UNSIGNED NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, hymn_id), KEY idx_favorites_user_created (user_id, created_at)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"""
            )
            await cursor.execute(
                """CREATE TABLE IF NOT EXISTS user_quick_songbooks (
                    user_id BIGINT NOT NULL, songbook_id INT UNSIGNED NOT NULL,
                    position INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, songbook_id), KEY idx_quick_user_position (user_id, position)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"""
            )
