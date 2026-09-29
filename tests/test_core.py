import unittest

import core


class TestCore(unittest.TestCase):
    def test_01_no_duplicate_observation(self):
        state = core.new_game()
        self.assertTrue(core.observe(state, "O1", "火星"))
        self.assertFalse(core.observe(state, "O1", "火星"))

    def test_02_no_schedule_in_bad_weather(self):
        state = core.new_game()
        state["weather"] = "cloudy"
        result = core.schedule(state, "W1")
        self.assertFalse(result)

    def test_03_storage_by_size_not_count(self):
        state = core.new_game()
        self.assertTrue(core.store(state, "A", 6))
        result = core.store(state, "B", 6)
        self.assertFalse(result)

    def test_04_calibrate_sets_flag(self):
        state = core.new_game()
        core.calibrate(state)
        self.assertTrue(state["calibrated"])

    def test_05_cancel_releases_window(self):
        state = core.new_game()
        state["windows"]["W1"] = "booked"
        core.cancel(state, "W1")
        self.assertEqual(state["windows"]["W1"], "open")

    def test_06_no_record_when_fault(self):
        state = core.new_game()
        state["fault"] = True
        result = core.record(state, "O1", 5)
        self.assertFalse(result)
        self.assertNotIn("O1", state["storage"])

    def test_07_weather_sequence_order(self):
        state = core.new_game()
        self.assertEqual(core.next_weather(state), "clear")
        self.assertEqual(core.next_weather(state), "cloudy")

    def test_08_load_preserves_day(self):
        state = core.new_game()
        state["day"] = 5
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded["day"], 5)


if __name__ == "__main__":
    unittest.main()
