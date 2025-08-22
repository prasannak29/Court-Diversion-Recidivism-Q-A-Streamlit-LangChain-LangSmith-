import json, time, statistics
from pathlib import Path
from typing import List, Dict, Any

DEFAULT_PATH = Path("metrics.jsonl")

def log_metrics(m: Dict[str, Any], path: Path = DEFAULT_PATH):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(m) + "\n")

def read_metrics(path: Path = DEFAULT_PATH) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows

def p95(values: List[float]) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = int(round(0.95 * (len(values) - 1)))
    return values[idx]

def aggregate(path: Path = DEFAULT_PATH) -> Dict[str, Any]:
    rows = read_metrics(path)
    if not rows:
        return {
            "count": 0,
            "throughput_qpm": 0.0,
            "p95_latency_s": 0.0,
            "avg_cost_usd": 0.0,
        }
    latencies = [r.get("latency_seconds", 0.0) for r in rows]
    costs = [r.get("cost_est_usd", 0.0) for r in rows]
    # Throughput: queries per minute over the last 15 minutes
    cutoff = time.time() - 15*60
    recent = [r for r in rows if r.get("ts", 0) >= cutoff]
    qpm = len(recent) / 15.0
    return {
        "count": len(rows),
        "throughput_qpm": round(qpm, 3),
        "p95_latency_s": round(p95(latencies), 3),
        "avg_cost_usd": round(sum(costs)/len(costs), 6) if costs else 0.0,
    }
