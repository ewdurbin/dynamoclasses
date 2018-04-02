
from dataclasses import dataclass


def _process_class(cls, *, table_name, partition_key, sort_key, data_class_kwargs):

    data_class = dataclass(cls, **data_class_kwargs)

    setattr(
        data_class,
        "__dynamoclass_params__",
        {
            "table_name": table_name,
            "partition_key": partition_key,
            "sort_key": sort_key,
        },
    )

    def save(cls):
        return f"saving: partition_key={cls.__dynamoclass_params__['partition_key']} sort_key={cls.__dynamoclass_params__['sort_key']} table_name={cls.__dynamoclass_params__['table_name']}"

    @classmethod
    def get(cls, *, partition_key, sort_key):
        return f"fetching: partition_key={partition_key} sort_key={sort_key} table_name={table_name}"

    data_class.save = save
    data_class.get = get

    return data_class


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
