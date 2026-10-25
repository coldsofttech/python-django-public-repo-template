# Databases

The database is chosen with one environment variable, `DATABASE_URL`. Without it, a SQLite file (`db.sqlite3` in `EXAMPLE_DATA_DIR`) is used, which is fine for development and small tools.

| Database | `DATABASE_URL` | Driver | Install |
| --- | --- | --- | --- |
| SQLite | `sqlite:///db.sqlite3` | built in | nothing |
| PostgreSQL | `postgres://user:password@host:5432/name` | psycopg 3 | `uv sync --extra postgres` |
| MySQL / MariaDB | `mysql://user:password@host:3306/name` | mysqlclient | `uv sync --extra mysql` |
| Oracle | `oracle://user:password@host:1521/service` | python-oracledb | `uv add oracledb` |
| Others | see the backend's documentation | its Django backend | `uv add <backend>` |

Any database Django supports works: install the backend package, set `DATABASE_URL` (or edit `DATABASES` in `settings.py` for options a URL cannot carry), and run the migrations.

## Migrations

```bash
uv run example-manage makemigrations     # after changing models
uv run example-manage migrate            # apply them
```

CI fails when a model change has no migration (`makemigrations --check`). Run `migrate` as a separate step on deploy, not inside the web process. The compose file shows this with a one-off `migrate` service.

## How the template is tested

- Unit tests run on SQLite on every supported Python version and operating system.
- The same test suite runs against **PostgreSQL** and **MySQL** service containers in CI.
- To run it yourself: `DATABASE_URL=postgres://... uv run pytest` after installing the extra.

## MySQL notes

`mysqlclient` is compiled, so install the client library first (Debian and Ubuntu: `sudo apt-get install pkg-config default-libmysqlclient-dev`; macOS: `brew install mysql-client pkg-config`). The Docker image builds it for you when you pass `--build-arg UV_EXTRAS="--extra mysql"`.

## Docker image variants

The image includes PostgreSQL support by default. Choose another set at build time:

```bash
docker build --build-arg UV_EXTRAS="--extra mysql" -t myapp .
docker build --build-arg UV_EXTRAS="" -t myapp .      # SQLite only
```

For the published GHCR image, set the repository variable `DOCKER_UV_EXTRAS` (see [development](development.md)).

## Connections

Connections stay open for `EXAMPLE_DB_CONN_MAX_AGE` seconds and are health-checked before reuse. With many server processes, put a pooler such as PgBouncer in front of PostgreSQL.
