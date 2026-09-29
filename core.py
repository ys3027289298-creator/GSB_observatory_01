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
    if state["weather"] != "clear":
        return False
    if state["windows"].get(window) != "open":
        return False
    state["windows"][window] = "booked"
    return True


def _storage_used(state):
    return sum(state["storage"].values())


def store(state, obs_id, size):
    if not obs_id or not isinstance(size, int) or size <= 0:
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
    if state["windows"].get(window) != "booked":
        return False
    state["windows"][window] = "open"
    return True


def record(state, obs_id, size):
    if state["fault"]:
        return False
    return store(state, obs_id, size)


def next_weather(state):
    seq = state["weather_seq"]
    weather = seq[state["weather_idx"] % len(seq)]
    state["weather_idx"] += 1
    state["weather"] = weather
    return weather


def main():
    state = new_game()
    usage = "observe/schedule/store/calibrate/cancel/record/weather/quit"
    print("天文台 - 命令: " + usage)
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            print("空命令，可用: " + usage)
            continue
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        if cmd == "quit" and not args:
            break
        elif cmd == "observe" and len(args) == 2:
            print("ok" if observe(state, args[0], args[1]) else "失败: 重复或非法观测")
        elif cmd == "schedule" and len(args) == 1:
            print("ok" if schedule(state, args[0]) else "失败: 天气不佳或窗口不可用")
        elif cmd == "store" and len(args) == 2 and args[1].isdigit():
            print("ok" if store(state, args[0], int(args[1])) else "失败: 容量不足或非法数据")
        elif cmd == "calibrate" and not args:
            calibrate(state)
            print("ok")
        elif cmd == "cancel" and len(args) == 1:
            print("ok" if cancel(state, args[0]) else "失败: 窗口未预订")
        elif cmd == "record" and len(args) == 2 and args[1].isdigit():
            print("ok" if record(state, args[0], int(args[1])) else "失败: 设备故障或容量不足")
        elif cmd == "weather" and not args:
            print(next_weather(state))
        else:
            print("未知命令: " + raw)


if __name__ == "__main__":
    main()
