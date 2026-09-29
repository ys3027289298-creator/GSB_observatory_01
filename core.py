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
    return json.loads(text)


def observe(state, obs_id, target):
    if not obs_id or not target:
        return False
    if obs_id in state["observations"]:
        return False
    state["observations"][obs_id] = target
    return True


def schedule(state, window):
    if window not in state["windows"]:
        return False
    if state["weather"] != "clear":
        return False
    if state["windows"][window] != "open":
        return False
    state["windows"][window] = "booked"
    return True


def _storage_used(state):
    return sum(state["storage"].values())


def store(state, obs_id, size):
    if not obs_id:
        return False
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        return False
    if obs_id in state["storage"]:
        return False
    if _storage_used(state) + size > state["storage_capacity"]:
        return False
    state["storage"][obs_id] = size
    return True


def calibrate(state):
    state["calibrated"] = True
    return True


def cancel(state, window):
    if window not in state["windows"]:
        return False
    if state["windows"][window] == "booked":
        state["windows"][window] = "open"
    return True


def record(state, obs_id, size):
    if state.get("fault"):
        return False
    if not obs_id:
        return False
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        return False
    if _storage_used(state) + size > state["storage_capacity"]:
        return False
    current = state["storage"].get(obs_id, 0)
    state["storage"][obs_id] = current + size
    return True


def next_weather(state):
    weather = state["weather_seq"][state["weather_idx"]]
    state["weather"] = weather
    state["weather_idx"] = (state["weather_idx"] + 1) % len(state["weather_seq"])
    return weather


def _parse_int(text):
    try:
        return int(text)
    except (TypeError, ValueError):
        return None


def main():
    print("天文台 - 命令: observe/schedule/store/calibrate/cancel/record/weather/quit")
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw == "quit":
            break
        parts = raw.split()
        command = parts[0]
        args = parts[1:]
        if command == "observe":
            if len(args) < 2:
                print("参数错误")
                continue
            print("ok" if observe(state, args[0], " ".join(args[1:])) else "失败")
        elif command == "schedule":
            if len(args) != 1:
                print("参数错误")
                continue
            print("ok" if schedule(state, args[0]) else "失败")
        elif command == "store":
            if len(args) != 2 or _parse_int(args[1]) is None:
                print("参数错误")
                continue
            print("ok" if store(state, args[0], _parse_int(args[1])) else "失败")
        elif command == "calibrate":
            calibrate(state)
            print("ok")
        elif command == "cancel":
            if len(args) != 1:
                print("参数错误")
                continue
            print("ok" if cancel(state, args[0]) else "失败")
        elif command == "record":
            if len(args) != 2 or _parse_int(args[1]) is None:
                print("参数错误")
                continue
            print("ok" if record(state, args[0], _parse_int(args[1])) else "失败")
        elif command == "weather":
            print(next_weather(state))
        else:
            print("未知命令")


if __name__ == "__main__":
    main()
