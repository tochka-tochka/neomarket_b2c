from src.services.categories.get import session, B2B_HOST


def make_filters_query_params(filters: dict[str, list[str]]) -> list[str]:
    r = []
    for filter_name, filter_values in filters.items():
        for val in filter_values:
            r.append(f"filters[{filter_name}]={val}")
    return r


def get_catalog_facets(category_id, filters: dict[str, list[str]]):
    filters_string = "&".join(make_filters_query_params(filters))
    r = session.get(f"http://{B2B_HOST}/api/v1/catalog/facets?category_id={category_id}&" + filters_string)
    return r.json()
