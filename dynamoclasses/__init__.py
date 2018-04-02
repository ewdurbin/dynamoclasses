
from dataclasses import dataclass


def _process_class(cls, *, table_name, partition_key, sort_key, data_class_kwargs):

    data_class = dataclass(cls, **data_class_kwargs)

    class DynamoClass(data_class):

        def save(self):
            return f"saving: partition_key={partition_key} table_name={table_name}"

    return DynamoClass


def dynamoclass(
    _cls=None, *, table_name=None, partition_key=None, sort_key=None, **kwargs
):

    def wrap(cls):
        return _process_class(
            cls,
            table_name=table_name,
            partition_key=partition_key,
            sort_key=sort_key,
            data_class_kwargs=kwargs,
        )

    if _cls is None:
        return wrap

    return wrap(_cls)
