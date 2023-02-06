from kopf import on
from src.init_kubernetes_config import initialize_kube
from src.functions import get_spec_and_primary_id, execute_sql_command
from src.db_client import postgres_client_from_env

initialize_kube()
psql_client = postgres_client_from_env()

@on.create("writer.opso.io", "v1", "pgdb-writer")
def create_fn(spec, **kwargs):
    spec, primary_id = get_spec_and_primary_id(kwargs)
    return execute_sql_command(psql_client.insert_row, spec, primary_id)

@on.update("writer.opso.io", "v1", "pgdb-writer")
def update_fn(spec, **kwargs):
    spec, primary_id = get_spec_and_primary_id(kwargs)
    return execute_sql_command(psql_client.update_row, spec, primary_id)

@on.delete("writer.opso.io", "v1", "pgdb-writer")
def delete_fn(spec, **kwargs):
    spec, primary_id = get_spec_and_primary_id(kwargs)
    table = spec["table"]
    psql_client.delete_row(table, primary_id)
    return "Successfully delete data corresponding to id: {id}".format(id=primary_id)