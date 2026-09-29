import unittest

import core


class TestRegression(unittest.TestCase):
    def test_invalid_window_rejected(self):
        state = core.new_game()
        self.assertFalse(core.schedule(state, "W9"))
        self.assertFalse(core.cancel(state, "W9"))
        self.assertNotIn("W9", state["windows"])

    def test_observe_empty_data(self):
        state = core.new_game()
        self.assertFalse(core.observe(state, "", "火星"))
        self.assertFalse(core.observe(state, "O1", ""))
        self.assertEqual(state["observations"], {})

    def test_store_empty_and_nonpositive(self):
        state = core.new_game()
        self.assertFalse(core.store(state, "", 5))
        self.assertFalse(core.store(state, "A", 0))
        self.assertFalse(core.store(state, "A", -1))
        self.assertEqual(state["storage"], {})

    def test_storage_capacity_boundary(self):
        state = core.new_game()
        self.assertTrue(core.store(state, "A", 6))
        self.assertTrue(core.store(state, "B", 4))
        self.assertFalse(core.store(state, "C", 1))

    def test_duplicate_inputs_rejected(self):
        state = core.new_game()
        self.assertTrue(core.observe(state, "O1", "火星"))
        self.assertFalse(core.observe(state, "O1", "木星"))
        self.assertTrue(core.store(state, "O1", 3))
        self.assertFalse(core.store(state, "O1", 3))
        self.assertTrue(core.schedule(state, "W1"))
        self.assertFalse(core.schedule(state, "W1"))

    def test_record_fault_then_capacity(self):
        state = core.new_game()
        state["fault"] = True
        self.assertFalse(core.record(state, "O1", 1))
        state["fault"] = False
        self.assertTrue(core.record(state, "O1", 10))
        self.assertFalse(core.record(state, "O2", 1))

    def test_weather_fixed_sequence_cycles(self):
        state = core.new_game()
        got = [core.next_weather(state) for _ in range(4)]
        self.assertEqual(got, ["clear", "cloudy", "storm", "clear"])
        self.assertEqual(state["weather"], "clear")

    def test_save_load_roundtrip(self):
        state = core.new_game()
        state["day"] = 3
        state["calibrated"] = True
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded, state)


if __name__ == "__main__":
    unittest.main()
