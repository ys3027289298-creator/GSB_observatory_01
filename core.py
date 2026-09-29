"""天文台核心逻辑：望远镜、观测窗口、天气、数据存储和校准。"""

import json


def new_game():
    return {
        "observations": {},
        "windows": {"W1": "open", "W2": "open"},
        "weather": "clear",
        "storage": {},
        "storage_capacity": 10,
        "calibrated": False,
        "day": 1,
        "fault": False,
        "weather_seq": ["clear", "cloudy", "storm"],
        "weather_idx": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    state["day"] += 1
    return state


def observe(state, obs_id, target):
    state["observations"][obs_id] = target
    return True


def schedule(state, window):
    state["windows"][window] = "booked"
    return True


def store(state, obs_id, size):
    if len(state["storage"]) >= state["storage_capacity"]:
        return False
    state["storage"][obs_id] = size
    return True


def calibrate(state):
    return True


def cancel(state, window):
    return True


def record(state, obs_id, size):
    state["storage"][obs_id] = size
    return True


def next_weather(state):
    state["weather_idx"] += 1
    return state["weather_seq"][-1]


def main():
    print("天文台 - 命令: observe/schedule/store/calibrate/cancel/record/weather/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
