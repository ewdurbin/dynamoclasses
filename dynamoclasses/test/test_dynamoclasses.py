import unittest


from dynamoclasses import dynamoclass


class DynamoClassTestCase(unittest.TestCase):

    def test_init(self):

        @dynamoclass
        class InventoryItem:
            name: str

        item = InventoryItem("hammers")
        self.assertEqual(item.name, "hammers")

    def test_save(self):

        @dynamoclass(table_name="inventory", partition_key="partition", sort_key="sort")
        class InventoryItem:
            name: str

        item = InventoryItem("hammers")
        save_string = item.save()
        self.assertEqual(
            save_string,
            "saving: partition_key=partition sort_key=sort table_name=inventory",
        )
        get_string = item.get(partition_key="foo", sort_key="bar")
        self.assertEqual(
            get_string, "fetching: partition_key=foo sort_key=bar table_name=inventory"
        )


if __name__ == "__main__":
    unittest.main()
