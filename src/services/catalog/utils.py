import re
from collections import defaultdict

from django.http import QueryDict


def parse_query_filters(filter_param_name: str, query_dict: QueryDict) -> dict[str, list[str]]:
    result = defaultdict(list)
    for key in query_dict:
        r = re.search(filter_param_name + r"\[(\w+)\]", key)
        if r:
            result[r.group(1)].append(query_dict[key])

    return result
