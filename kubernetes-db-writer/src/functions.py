def get_spec_and_primary_id(kwargs):
    resource_namespace = kwargs["body"]["metadata"]["namespace"]
    resource_name = kwargs["body"]["metadata"]["name"]
    spec = kwargs["body"]["spec"]
    
    primary_id = resource_namespace + "/" + resource_name
    return spec,primary_id

def execute_sql_command(fn_with_object, spec, primary_id):
    table, name, registered, zipcode, country = spec["table"], spec["name"], spec["registered"], spec["zipcode"], spec["country"]

    fn_with_object(table, primary_id, name, registered, zipcode, country)
    
    return "Successfully wrote data corresponding to id: {id}, table: {table}, name: {name}, registered: {registered}, zipcode: {zipcode}, country: {country}".format(
        id=primary_id,
        table=table,
        name=name, 
        registered=registered, 
        zipcode=zipcode, 
        country=country
    )