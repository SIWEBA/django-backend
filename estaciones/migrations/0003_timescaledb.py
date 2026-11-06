from django.db import migrations

TIMESCALE_HELP = (
    'TimescaleDB no está disponible en este servidor PostgreSQL. '
    'Instálalo y habilítalo (ver docs/tecnica/instalar-timescaledb.md): '
    "paquete timescaledb-2-postgresql-<versión>, shared_preload_libraries = "
    "'timescaledb', reinicio y, como superusuario, "
    'CREATE EXTENSION timescaledb en esta base.'
)


def require_timescaledb(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT 1 FROM pg_available_extensions WHERE name = 'timescaledb'"
        )
        if cursor.fetchone() is None:
            raise RuntimeError(TIMESCALE_HELP)


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('estaciones', '0002_seed_roles_estacion'),
        ('usuarios', '0002_seed_roles_sistema'),
    ]

    operations = [
        migrations.RunPython(require_timescaledb, migrations.RunPython.noop),
        migrations.RunSQL(
            sql='CREATE EXTENSION IF NOT EXISTS timescaledb',
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql='ALTER TABLE lecturas SET (fillfactor = 90)',
            reverse_sql='ALTER TABLE lecturas RESET (fillfactor)',
        ),
        migrations.RunSQL(
            sql=(
                "SELECT create_hypertable("
                "'lecturas', by_range('fecha_hora', INTERVAL '7 days'), "
                "if_not_exists => TRUE)"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql=(
                "SELECT create_hypertable("
                "'telemetria_dispositivo', "
                "by_range('fecha_hora', INTERVAL '7 days'), "
                "if_not_exists => TRUE)"
            ),
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE FUNCTION upsert_lecturas(p_lecturas jsonb)
                RETURNS integer
                LANGUAGE plpgsql
                AS $$
                DECLARE
                    v_item jsonb;
                    v_row lecturas%ROWTYPE;
                    v_key text;
                    v_seen text[] := ARRAY[]::text[];
                    v_total integer := 0;
                BEGIN
                    IF jsonb_typeof(p_lecturas) IS DISTINCT FROM 'array' THEN
                        RAISE EXCEPTION 'p_lecturas debe ser un arreglo JSON';
                    END IF;

                    FOR v_item IN
                        SELECT item.value
                        FROM jsonb_array_elements(p_lecturas) AS item(value)
                    LOOP
                        v_row := jsonb_populate_record(NULL::lecturas, v_item);
                        v_key := v_row.estacion_id::text || '|' || v_row.fecha_hora::text;

                        INSERT INTO lecturas AS l
                        SELECT v_row.*
                        ON CONFLICT (estacion_id, fecha_hora) DO UPDATE SET
                            temp_ext = COALESCE(EXCLUDED.temp_ext, l.temp_ext),
                            temp_max = COALESCE(EXCLUDED.temp_max, l.temp_max),
                            temp_min = COALESCE(EXCLUDED.temp_min, l.temp_min),
                            hum_ext = COALESCE(EXCLUDED.hum_ext, l.hum_ext),
                            vel_viento = COALESCE(EXCLUDED.vel_viento, l.vel_viento),
                            dir_viento = COALESCE(EXCLUDED.dir_viento, l.dir_viento),
                            recorrido_viento = COALESCE(EXCLUDED.recorrido_viento, l.recorrido_viento),
                            vel_max_viento = COALESCE(EXCLUDED.vel_max_viento, l.vel_max_viento),
                            dir_vel_max = COALESCE(EXCLUDED.dir_vel_max, l.dir_vel_max),
                            lluvia = COALESCE(EXCLUDED.lluvia, l.lluvia),
                            tasa_lluvia = COALESCE(EXCLUDED.tasa_lluvia, l.tasa_lluvia),
                            rad_solar = COALESCE(EXCLUDED.rad_solar, l.rad_solar),
                            energia_solar = COALESCE(EXCLUDED.energia_solar, l.energia_solar),
                            rad_solar_max = COALESCE(EXCLUDED.rad_solar_max, l.rad_solar_max),
                            indice_uv = COALESCE(EXCLUDED.indice_uv, l.indice_uv),
                            dosis_uv = COALESCE(EXCLUDED.dosis_uv, l.dosis_uv),
                            uv_max = COALESCE(EXCLUDED.uv_max, l.uv_max),
                            presion_bar = COALESCE(EXCLUDED.presion_bar, l.presion_bar),
                            punto_rocio = COALESCE(EXCLUDED.punto_rocio, l.punto_rocio),
                            sensacion_termica = COALESCE(EXCLUDED.sensacion_termica, l.sensacion_termica),
                            indice_calor = COALESCE(EXCLUDED.indice_calor, l.indice_calor),
                            indice_thw = COALESCE(EXCLUDED.indice_thw, l.indice_thw),
                            indice_thsw = COALESCE(EXCLUDED.indice_thsw, l.indice_thsw),
                            evapotranspiracion = COALESCE(EXCLUDED.evapotranspiracion, l.evapotranspiracion),
                            temp_int = COALESCE(EXCLUDED.temp_int, l.temp_int),
                            hum_int = COALESCE(EXCLUDED.hum_int, l.hum_int),
                            recepcion_iss = COALESCE(EXCLUDED.recepcion_iss, l.recepcion_iss),
                            int_archivo = COALESCE(EXCLUDED.int_archivo, l.int_archivo);

                        IF NOT (v_key = ANY(v_seen)) THEN
                            v_seen := array_append(v_seen, v_key);
                            v_total := v_total + 1;
                        END IF;
                    END LOOP;

                    RETURN v_total;
                END;
                $$
            """,
            reverse_sql='DROP FUNCTION IF EXISTS upsert_lecturas(jsonb)',
        ),
        migrations.RunSQL(
            sql=(
                "ALTER TABLE lecturas SET ("
                "timescaledb.compress, "
                "timescaledb.compress_segmentby = 'estacion_id', "
                "timescaledb.compress_orderby = 'fecha_hora DESC')"
            ),
            reverse_sql=(
                "ALTER TABLE lecturas RESET ("
                "timescaledb.compress, "
                "timescaledb.compress_segmentby, "
                "timescaledb.compress_orderby)"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "SELECT add_compression_policy("
                "'lecturas', compress_after => INTERVAL '90 days', "
                "if_not_exists => TRUE)"
            ),
            reverse_sql=(
                "SELECT remove_compression_policy('lecturas', if_exists => TRUE)"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "ALTER TABLE telemetria_dispositivo SET ("
                "timescaledb.compress, "
                "timescaledb.compress_segmentby = 'subestacion_id', "
                "timescaledb.compress_orderby = 'fecha_hora DESC')"
            ),
            reverse_sql=(
                "ALTER TABLE telemetria_dispositivo RESET ("
                "timescaledb.compress, "
                "timescaledb.compress_segmentby, "
                "timescaledb.compress_orderby)"
            ),
        ),
        migrations.RunSQL(
            sql=(
                "SELECT add_compression_policy("
                "'telemetria_dispositivo', "
                "compress_after => INTERVAL '90 days', if_not_exists => TRUE)"
            ),
            reverse_sql=(
                "SELECT remove_compression_policy("
                "'telemetria_dispositivo', if_exists => TRUE)"
            ),
        ),
        migrations.RunSQL(
            sql="""
                CREATE MATERIALIZED VIEW IF NOT EXISTS lecturas_hora
                WITH (timescaledb.continuous) AS
                SELECT
                    estacion_id,
                    time_bucket('1 hour', fecha_hora) AS hora,
                    avg(temp_ext)::real AS temp_prom,
                    max(temp_ext) AS temp_max,
                    min(temp_ext) AS temp_min,
                    avg(hum_ext)::real AS hum_prom,
                    avg(presion_bar)::real AS presion_prom,
                    avg(vel_viento)::real AS viento_prom,
                    max(vel_max_viento) AS racha_max,
                    sum(lluvia)::double precision AS lluvia_total,
                    max(tasa_lluvia) AS tasa_lluvia_max,
                    avg(rad_solar)::real AS rad_solar_prom,
                    max(indice_uv) AS uv_max,
                    count(*) AS num_lecturas
                FROM lecturas
                GROUP BY estacion_id, hora
                WITH NO DATA
            """,
            reverse_sql='DROP MATERIALIZED VIEW IF EXISTS lecturas_hora',
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS idx_lecturas_hora_estacion "
                "ON lecturas_hora (estacion_id, hora DESC)"
            ),
            reverse_sql='DROP INDEX IF EXISTS idx_lecturas_hora_estacion',
        ),
        migrations.RunSQL(
            sql=(
                "SELECT add_continuous_aggregate_policy("
                "'lecturas_hora', start_offset => INTERVAL '3 days', "
                "end_offset => INTERVAL '1 hour', "
                "schedule_interval => INTERVAL '30 minutes', "
                "if_not_exists => TRUE)"
            ),
            reverse_sql=(
                "SELECT remove_continuous_aggregate_policy("
                "'lecturas_hora', if_exists => TRUE)"
            ),
        ),
        migrations.RunSQL(
            sql='ALTER MATERIALIZED VIEW lecturas_hora SET (timescaledb.compress = true)',
            reverse_sql='ALTER MATERIALIZED VIEW lecturas_hora RESET (timescaledb.compress)',
        ),
        migrations.RunSQL(
            sql=(
                "SELECT add_compression_policy("
                "'lecturas_hora', compress_after => INTERVAL '30 days', "
                "if_not_exists => TRUE)"
            ),
            reverse_sql=(
                "SELECT remove_compression_policy("
                "'lecturas_hora', if_exists => TRUE)"
            ),
        ),
        migrations.RunSQL(
            sql="""
                CREATE MATERIALIZED VIEW IF NOT EXISTS lecturas_dia
                WITH (timescaledb.continuous) AS
                SELECT
                    estacion_id,
                    time_bucket('1 day', fecha_hora) AS dia,
                    avg(temp_ext)::real AS temp_prom,
                    max(temp_ext) AS temp_max,
                    min(temp_ext) AS temp_min,
                    avg(hum_ext)::real AS hum_prom,
                    avg(presion_bar)::real AS presion_prom,
                    avg(vel_viento)::real AS viento_prom,
                    max(vel_max_viento) AS racha_max,
                    sum(lluvia)::double precision AS lluvia_total,
                    max(tasa_lluvia) AS tasa_lluvia_max,
                    avg(rad_solar)::real AS rad_solar_prom,
                    max(indice_uv) AS uv_max,
                    count(*) AS num_lecturas
                FROM lecturas
                GROUP BY estacion_id, dia
                WITH NO DATA
            """,
            reverse_sql='DROP MATERIALIZED VIEW IF EXISTS lecturas_dia',
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS idx_lecturas_dia_estacion "
                "ON lecturas_dia (estacion_id, dia DESC)"
            ),
            reverse_sql='DROP INDEX IF EXISTS idx_lecturas_dia_estacion',
        ),
        migrations.RunSQL(
            sql=(
                "SELECT add_continuous_aggregate_policy("
                "'lecturas_dia', start_offset => INTERVAL '7 days', "
                "end_offset => INTERVAL '1 day', "
                "schedule_interval => INTERVAL '1 hour', "
                "if_not_exists => TRUE)"
            ),
            reverse_sql=(
                "SELECT remove_continuous_aggregate_policy("
                "'lecturas_dia', if_exists => TRUE)"
            ),
        ),
    ]
