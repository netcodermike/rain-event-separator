from datetime import datetime, timedelta
from math import isfinite

def analyze(data):
    gap = data["gapHours"]
    if type(gap) not in (int,float) or not isfinite(gap) or not 0 < gap < 8760:
        raise ValueError("gapHours must be between zero and 8760")
    readings = []
    for stamp, amount in data["readings"]:
        moment = datetime.fromisoformat(stamp)
        if moment.utcoffset() is None or type(amount) not in (int,float) or not isfinite(amount) or not 0 <= amount <= 10000:
            raise ValueError("Invalid rainfall reading")
        readings.append((moment, amount))
    if len({moment for moment, _ in readings}) != len(readings):
        raise ValueError("Duplicate timestamp")
    storms = []
    last = None
    for moment, amount in sorted(readings):
        if not amount:
            continue
        if last is None or moment - last >= timedelta(hours=gap):
            storms.append({"start":moment.isoformat(), "end":moment.isoformat(), "mm":0})
        storms[-1]["end"] = moment.isoformat()
        storms[-1]["mm"] += amount
        last = moment
    return {"events":len(storms),"totalMm":round(sum(item["mm"] for item in storms),4),"storms":storms}

if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys
    try:
        path, = sys.argv[1:]
        result = analyze(json.loads(Path(path).read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        sys.exit(2)
