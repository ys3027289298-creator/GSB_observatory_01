import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

import core


class TestRegression(unittest.TestCase):
    def test_observe_empty_data(self):
        state = core.new_game()
        self.assertFalse(core.observe(state, "", "火星"))
        self.assertFalse(core.observe(state, "O1", ""))
        self.assertNotIn("O1", state["observations"])

    def test_duplicate_observation_other_target(self):
        state = core.new_game()
        self.assertTrue(core.observe(state, "O1", "火星"))
        self.assertFalse(core.observe(state, "O1", "金星"))
        self.assertEqual(state["observations"]["O1"], "火星")

    def test_storage_capacity_boundary(self):
        state = core.new_game()
        self.assertTrue(core.store(state, "A", 6))
        self.assertTrue(core.store(state, "B", 4))
        self.assertEqual(core._storage_used(state), 10)
        self.assertFalse(core.store(state, "C", 1))

    def test_storage_rejects_empty_zero_negative(self):
        state = core.new_game()
        self.assertFalse(core.store(state, "", 1))
        self.assertFalse(core.store(state, "A", 0))
        self.assertFalse(core.store(state, "A", -3))
        self.assertNotIn("A", state["storage"])

    def test_duplicate_store_id(self):
        state = core.new_game()
        self.assertTrue(core.store(state, "A", 4))
        self.assertFalse(core.store(state, "A", 2))
        self.assertEqual(state["storage"]["A"], 4)

    def test_schedule_duplicate_and_unknown_window(self):
        state = core.new_game()
        self.assertTrue(core.schedule(state, "W1"))
        self.assertFalse(core.schedule(state, "W1"))
        self.assertFalse(core.schedule(state, "WX"))

    def test_schedule_after_storm_then_clear(self):
        state = core.new_game()
        core.next_weather(state)
        core.next_weather(state)
        core.next_weather(state)
        self.assertEqual(state["weather"], "storm")
        self.assertFalse(core.schedule(state, "W1"))
        core.next_weather(state)
        self.assertEqual(state["weather"], "clear")
        self.assertTrue(core.schedule(state, "W1"))

    def test_cancel_unknown_window(self):
        state = core.new_game()
        self.assertFalse(core.cancel(state, "WX"))

    def test_record_accumulates_valid_data(self):
        state = core.new_game()
        self.assertTrue(core.record(state, "O1", 3))
        self.assertTrue(core.record(state, "O1", 4))
        self.assertEqual(state["storage"]["O1"], 7)

    def test_record_fault_does_not_accumulate(self):
        state = core.new_game()
        self.assertTrue(core.record(state, "O1", 3))
        state["fault"] = True
        self.assertFalse(core.record(state, "O1", 4))
        self.assertEqual(state["storage"]["O1"], 3)

    def test_weather_full_cycle_is_stable(self):
        state = core.new_game()
        seen = [core.next_weather(state) for _ in range(7)]
        self.assertEqual(
            seen,
            ["clear", "cloudy", "storm", "clear", "cloudy", "storm", "clear"],
        )

    def test_calibrate_is_sticky(self):
        state = core.new_game()
        core.calibrate(state)
        self.assertTrue(state["calibrated"])
        loaded = core.load_state(core.save_state(state))
        self.assertTrue(loaded["calibrated"])

    def test_save_load_round_trip(self):
        state = core.new_game()
        core.observe(state, "O1", "火星")
        core.store(state, "O1", 5)
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded, state)

    def test_menu_unknown_and_empty_commands(self):
        state = core.new_game()
        answers = ["bogus", "", "schedule", "schedule W1", "quit"]
        out = io.StringIO()
        with mock.patch("builtins.input", side_effect=answers), \
                mock.patch.object(core, "new_game", return_value=state), \
                redirect_stdout(out):
            core.main()
        text = out.getvalue()
        self.assertIn("未知命令", text)
        self.assertIn("参数错误", text)
        self.assertIn("ok", text)
        self.assertEqual(state["windows"]["W1"], "booked")


if __name__ == "__main__":
    unittest.main()
