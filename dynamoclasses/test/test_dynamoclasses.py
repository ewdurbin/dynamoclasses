import unittest

from dynamoclasses import dynamoclass

import botocore

from moto import mock_dynamodb2


class DynamoClassTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock = mock_dynamodb2()
        cls.mock.start()
        cls.session = botocore.session.get_session()
        cls.client = cls.session.create_client("dynamodb")
        cls.client.create_table(
            TableName="inventory",
            KeySchema=[{"AttributeName": "item_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "item_id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
        )

    @classmethod
    def tearDownClass(cls):
        cls.mock.stop()

    def test_init(self):

        with self.assertRaises(Exception):

            @dynamoclass
            class InventoryItem:
                name: str

    def test_init_options(self):

        with self.assertRaises(Exception):

            @dynamoclass(
                table_name="inventory",
                partition_key_name="partition",
                sort_key_name="sort",
            )
            class InventoryItem:
                name: str

    def test_init_with_valid_options(self):

        @dynamoclass(table_name="inventory", partition_key_name="item_id")
        class InventoryItem:
            item_id: str

        item = InventoryItem(item_id="000011123")
        self.assertEqual(
            item.__dynamoclass_params__,
            {
                "table_name": "inventory",
                "partition_key_name": "item_id",
                "sort_key_name": None,
            },
        )

    def test_save(self):

        @dynamoclass(table_name="inventory", partition_key_name="item_id")
        class InventoryItem:
            item_id: str

        item = InventoryItem(item_id="hammers")
        item.save()
        dynamo_item = self.client.get_item(
            TableName="inventory", Key={"item_id": {"S": "hammers"}}
        )
        self.assertEqual({"item_id": {"S": "hammers"}}, dynamo_item["Item"])

    def test_get(self):

        @dynamoclass(table_name="inventory", partition_key_name="item_id")
        class InventoryItem:
            item_id: str

        dynamo_item = self.client.put_item(
            TableName="inventory", Item={"item_id": {"S": "nails"}}
        )
        item = InventoryItem.get(partition_key="nails", sort_key=None)
        self.assertEqual("nails", item.item_id)


if __name__ == "__main__":
    unittest.main()
