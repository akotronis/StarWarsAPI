import io

from django.db import connection


def id_from_swapi_detail_url(url):
    """
    From a swapi detail url extract last item from path.
    Args:
        url (str): A swapi detail url

    Returns:
        int: The resource id as int
    """
    return int(url.split("/")[-1])


def copy_insert(model, rows, columns):
    """
    Perform a fast bulk insert into a Django model's database table using
    PostgreSQL's COPY command.

    Args:
        model (django.db.models.Model): The Django model class representing the table.
        rows (list[tuple]): Sequence of row values to insert. Each tuple must match
            the order of the given `columns`.
        columns (list[str]): Names of the database columns to insert into.

    Notes:
        - Uses an in-memory buffer (StringIO) to batch all rows into a tab-delimited
          format and then streams them directly into PostgreSQL with `COPY FROM`.
        - `None` values in Python are translated to Postgres `NULL` using the `\\N`
          marker.
        - `buf.seek(0)` is required after writing, because COPY reads from the current
          cursor position. Without rewinding, COPY would start at the end of the
          buffer and insert zero rows.
        - This bypasses Django's ORM (`bulk_create`) for maximum speed, at the cost
          of skipping model `save()`, field defaults, `auto_now/auto_now_add`,
          and signal dispatch.
    """
    table = model._meta.db_table
    buf = io.StringIO()
    for row in rows:
        formatted = []
        for v in row:
            if v is None:
                formatted.append("\\N")
            else:
                formatted.append(str(v))
        buf.write("\t".join(formatted))
        buf.write("\n")
    buf.seek(0)

    with connection.cursor() as cursor:
        cursor.copy_from(buf, table, sep="\t", null="\\N", columns=columns)
