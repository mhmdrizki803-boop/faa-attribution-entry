import json, os, glob, math

IN = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

Z = [-1.6448536269514722, -0.6744897501960817, 0.0, 0.6744897501960817, 1.6448536269514722]

def forecast(prices, horizon):
    # median: last price (martingale); fallback 0.5 if no prices
    med = prices[-1] if prices else 0.5
    if med < 0.0: med = 0.0
    if med > 1.0: med = 1.0
    # per-minute sigma from last 960 one-minute differences
    n = min(len(prices) - 1, 960)
    if n > 0:
        diffs = [prices[i+1] - prices[i] for i in range(len(prices)-n, len(prices)-1)]
        m = sum(diffs) / n
        var = sum((d - m) ** 2 for d in diffs) / n
        sigma = math.sqrt(var) * 0.15
    else:
        sigma = 0.0003
    if sigma < 0.0003: sigma = 0.0003
    if sigma > 0.004: sigma = 0.004
    sigma *= 0.9
    rows = []
    for h in range(1, horizon + 1):
        hw = sigma * math.sqrt(h)
        row = []
        for z in Z:
            v = med + z * hw
            if v < 0.0: v = 0.0
            if v > 1.0: v = 1.0
            row.append(round(v, 6))
        for i in range(1, 5):
            if row[i] < row[i-1]:
                row[i] = row[i-1]
        rows.append(row)
    return rows

def main():
    os.makedirs(OUT, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(IN, "*.in"))):
        with open(path) as f:
            case = json.load(f)
        horizon = int(case.get("horizon_minutes", 240))
        markets = case.get("markets") or []
        out = []
        for mkt in markets:
            prices = mkt.get("prices") or []
            if not isinstance(prices, list) or not prices:
                prices = []
            out.append({"id": mkt.get("id"), "q": forecast(prices, horizon)})
        name = os.path.basename(path)
        with open(os.path.join(OUT, name[:-3] + ".out"), "w") as f:
            json.dump({"forecasts": out}, f)

if __name__ == "__main__":
    main()
# the fan claims: 80% of outcomes should land between the outer quantiles
