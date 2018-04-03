DynamoClasses
=============

API interface for [Amazon Web Services DynamoDB](https://aws.amazon.com/dynamodb/) built on top of [PEP 557 Data Classes](https://www.python.org/dev/peps/pep-0557/).

The goal is to have something that is fully a `dataclass` class, but gets some helpers bolted on allowing for retrieving/storing the objects in DynamoDB.

## Basic Usage

```python
>>> import botocore
>>>
>>> from moto import mock_dynamodb2
>>>
>>> from dynamoclasses import dynamoclass
>>>
>>> mock_dynamodb2().start()
>>>
>>> session = botocore.session.get_session()
>>> client = session.create_client("dynamodb")
>>> client.create_table(
...     TableName="inventory",
...     KeySchema=[
...         {"AttributeName": "item_id", "KeyType": "HASH"},
...     ],
...     AttributeDefinitions=[
...         {"AttributeName": "item_id", "AttributeType": "S"},
...     ],
...     ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
... )
{'TableDescription': ...}
>>>
>>> @dynamoclass(table_name="inventory", partition_key_name="item_id")
... class InventoryItem:
...     item_id: str
...
>>> item = InventoryItem("hammers")
>>> item.save()
{'Attributes': ...}
>>>
>>> found_item = InventoryItem.get(partition_key="hammers", sort_key=None)
>>>
>>> print(found_item.item_id)
hammers
