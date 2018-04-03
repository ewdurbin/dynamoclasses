
from dataclasses import dataclass, asdict

import boto3


TYPE_MAPPING = {
    str: {"key": "S", "fn": lambda x: str(x)},
    float: {"key": "N", "fn": lambda x: str(x)},
    int: {"key": "N", "fn": lambda x: str(x)},
    bytes: {"key": "B", "fn": lambda x: str(x)},
    dict: {"key": "M", "fn": lambda x: str(x)},
    bool: {"key": "BOOL", "fn": lambda x: x},
    None: {"key": "NULL", "fn": lambda x: x},
}


def _process_class(
    cls, *, table_name, partition_key_name, sort_key_name, data_class_kwargs
):

    data_class = dataclass(cls, **data_class_kwargs)

    if partition_key_name not in data_class.__dataclass_fields__:
        raise Exception(
            f'Partition Key Name "{partition_key_name}" not found in class fields'
        )

    if sort_key_name is not None and sort_key_name not in data_class.__dataclass_fields__:
        raise Exception(f'Sort Key Name "{sort_key_name}" not found in class fields')

    setattr(
        data_class,
        "__dynamoclass_params__",
        {
            "table_name": table_name,
            "partition_key_name": partition_key_name,
            "sort_key_name": sort_key_name,
        },
    )

    setattr(data_class, "__dynamoclass_client__", boto3.client("dynamodb"))

    def _format_to_dynamo(self):
        return {
            k: {TYPE_MAPPING[type(v)]["key"]: TYPE_MAPPING[type(v)]["fn"](v)}
            for k, v in asdict(self).items()
        }

    def save(self):
        return self.__dynamoclass_client__.put_item(
            TableName=self.__dynamoclass_params__["table_name"],
            Item=self._format_to_dynamo(),
        )

    @classmethod
    def _format_to_dataclass(cls, dynamodb_item):
        kwargs = {}
        for field_name, value in dynamodb_item.items():
            if field_name not in cls.__dataclass_fields__:
                raise ValueError(
                    f"Cannot render field with name {field_name}! "
                    f"No such field name found for {cls}!"
                )

            kwargs[field_name] = cls.__dataclass_fields__[field_name].type(
                list(value.values())[0]
            )
        return kwargs

    @classmethod
    def _render_to_type(cls, field_name, value):
        if field_name not in cls.__dataclass_fields__:
            raise ValueError(
                f"Cannot render field with name {field_name}! "
                f"No such field name found for {cls}!"
            )

        return {
            TYPE_MAPPING[cls.__dataclass_fields__[field_name].type][
                "key"
            ]: TYPE_MAPPING[
                cls.__dataclass_fields__[field_name].type
            ][
                "fn"
            ](
                cls.__dataclass_fields__[field_name].type(value)
            )
        }

    @classmethod
    def get(cls, *, partition_key, sort_key):
        key = {
            cls.__dynamoclass_params__["partition_key_name"]: cls._render_to_type(
                cls.__dynamoclass_params__["partition_key_name"], partition_key
            )
        }
        if cls.__dynamoclass_params__["sort_key_name"] is not None:
            key[cls.__dynamoclass_params__["sort_key_name"]] = cls._render_to_type(
                cls.__dynamoclass_params__["sort_key_name"], sort_key
            )
        item = cls.__dynamoclass_client__.get_item(
            TableName=cls.__dynamoclass_params__["table_name"], Key=key
        )
        return cls(**cls._format_to_dataclass(item["Item"]))

    data_class._format_to_dynamo = _format_to_dynamo
    data_class._format_to_dataclass = _format_to_dataclass
    data_class._render_to_type = _render_to_type
    data_class.save = save
    data_class.get = get

    return data_class


def dynamoclass(
    _cls=None, *, table_name=None, partition_key_name=None, sort_key_name=None, **kwargs
):

    def wrap(cls):
        return _process_class(
            cls,
            table_name=table_name,
            partition_key_name=partition_key_name,
            sort_key_name=sort_key_name,
            data_class_kwargs=kwargs,
        )

    if _cls is None:
        return wrap

    return wrap(_cls)
