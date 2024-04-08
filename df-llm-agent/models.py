from schematics.models import Model
from schematics.types import IntType, StringType, BooleanType, DictType, BaseType
from schematics.types.compound import ListType, ModelType

from config import config

OUTPUT_FORMAT_CSV = 'csv'
OUTPUT_FORMAT_JSON = 'json'

_sort_values = ['DESC', 'ASC']
_output_format = [OUTPUT_FORMAT_JSON, OUTPUT_FORMAT_CSV]
_fills = ['0', 'null', 'none']


class Query(Model):
    query_id = StringType(serialized_name="QUERY_ID", required=True)
    select = StringType(serialized_name="SELECT", required=True)
    where = StringType(serialized_name="WHERE", required=False, default="1=1")
    group_by = StringType(serialized_name="GROUP_BY", required=False)
    having = StringType(serialized_name="HAVING", required=False)
    metrics = ListType(StringType, serialized_name="METRICS", required=False)
    tags = ListType(StringType, serialized_name="TAGS", required=False)
    ctags = ListType(StringType, serialized_name="CTAGS", required=False)
    stags = ListType(StringType, serialized_name="STAGS", required=False)
    roles = ListType(StringType, serialized_name="ROLES", required=False)