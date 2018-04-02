import unittest


from dynamoclasses import dynamoclass


class DynamoClassTestCase(unittest.TestCase):

    def test_init(self):

        @dynamoclass
        class InventoryItem:
            name: str
            unit_price: float
            quantity_on_hand: int = 0

            def total_cost(self) -> float:
                return self.unit_price * self.quantity_on_hand

        item = InventoryItem("hammers", 10.49, 12)
        self.assertEqual(item.name, "hammers")

    def test_save(self):

        @dynamoclass(table_name="inventory", partition_key="name")
        class InventoryItem:
            name: str

        item = InventoryItem("hammers")
        save_string = item.save()
        self.assertEqual(save_string, "saving: partition_key=name table_name=inventory")


if __name__ == "__main__":
    unittest.main()
