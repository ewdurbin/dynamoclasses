
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

    def _to_dynamo(self):
        return {
            k: {TYPE_MAPPING[type(v)]["key"]: TYPE_MAPPING[type(v)]["fn"](v)}
            for k, v in asdict(self).items()
        }

    def save(self):
        return self.__dynamoclass_client__.put_item(
            TableName=self.__dynamoclass_params__["table_name"],
            Item=self._to_dynamo(),
        )

    @classmethod
    def _to_dataclass(cls, dynamodb_item):
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
    def _dataclass_field_to_dynamo_field(cls, field_name, value):
        if field_name not in cls.__dataclass_fields__:
            raise ValueError(
                f"Cannot render field with name {field_name}! "
                f"No such field name found for {cls}!"
            )

        field_type = cls.__dataclass_fields__[field_name].type
        mapping = TYPE_MAPPING[field_type]

        dynamo_type =  mapping["key"]
        dynamo_value = mapping["fn"](field_type(value))

        return {dynamo_type: dynamo_value}

    @classmethod
    def get(cls, *, partition_key, sort_key):
        partition_key_name = cls.__dynamoclass_params__["partition_key_name"]
        sort_key_name = cls.__dynamoclass_params__["sort_key_name"]
        table_name = cls.__dynamoclass_params__["table_name"]
        key = {
            partition_key_name: cls._dataclass_field_to_dynamo_field(
                partition_key_name, partition_key
            )
        }
        if sort_key_name is not None:
            key[sort_key_name] = cls._dataclass_field_to_dynamo_field(
                sort_key_name, sort_key
            )
        item = cls.__dynamoclass_client__.get_item(
            TableName=table_name, Key=key
        )
        return cls(**cls._to_dataclass(item["Item"]))

    data_class._to_dynamo = _to_dynamo
    data_class._to_dataclass = _to_dataclass
    data_class._dataclass_field_to_dynamo_field = _dataclass_field_to_dynamo_field
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
