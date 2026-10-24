"""Recherche plein texte française insensible aux accents (`fr_unaccent`)."""
from django.db import migrations

CREATE_CONFIG = """
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_ts_config WHERE cfgname = 'fr_unaccent') THEN
        CREATE TEXT SEARCH CONFIGURATION fr_unaccent (COPY = french);
        ALTER TEXT SEARCH CONFIGURATION fr_unaccent
            ALTER MAPPING FOR hword, hword_part, word WITH unaccent, french_stem;
    END IF;
END
$$;
"""

DROP_CONFIG = "DROP TEXT SEARCH CONFIGURATION IF EXISTS fr_unaccent;"

REINDEX = """
UPDATE knowledge_knowledgechunk
SET search_vector =
    setweight(to_tsvector('fr_unaccent', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('fr_unaccent', coalesce(content, '')), 'B');
"""


class Migration(migrations.Migration):

    dependencies = [
        ("knowledge", "0003_knowledgechunk_embedding_and_more"),
    ]

    operations = [
        migrations.RunSQL(CREATE_CONFIG, reverse_sql=DROP_CONFIG),
        migrations.RunSQL(REINDEX, reverse_sql=migrations.RunSQL.noop),
    ]
