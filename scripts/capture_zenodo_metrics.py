import csv
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"C:\Users\M7120\Documents\New project 7")
LOG_DIR = ROOT / "zenodo_metrics_log"
WATCHLIST = LOG_DIR / "zenodo_watchlist.csv"


def fetch_record(record):
    record_id = record["record_id"]
    url = f"https://zenodo.org/api/records/{record_id}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        stats = data.get("stats") or {}
        meta = data.get("metadata") or {}
        links = data.get("links") or {}
        return {
            "captured_at": CAPTURED_AT,
            "cluster": record.get("cluster", ""),
            "notes": record.get("notes", ""),
            "id": data.get("id", record_id),
            "doi": data.get("doi", ""),
            "title": meta.get("title", ""),
            "resource_type": (meta.get("resource_type") or {}).get("type", ""),
            "publication_date": meta.get("publication_date", ""),
            "version": meta.get("version", ""),
            "views": stats.get("views", ""),
            "unique_views": stats.get("unique_views", ""),
            "downloads": stats.get("downloads", ""),
            "unique_downloads": stats.get("unique_downloads", ""),
            "record_url": links.get("html", f"https://zenodo.org/records/{record_id}"),
            "status": "ok",
        }
    except Exception as exc:
        return {
            "captured_at": CAPTURED_AT,
            "cluster": record.get("cluster", ""),
            "notes": record.get("notes", ""),
            "id": record_id,
            "doi": "",
            "title": str(exc),
            "resource_type": "",
            "publication_date": "",
            "version": "",
            "views": "",
            "unique_views": "",
            "downloads": "",
            "unique_downloads": "",
            "record_url": f"https://zenodo.org/records/{record_id}",
            "status": "error",
        }


CAPTURED_AT = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with WATCHLIST.open(newline="", encoding="utf-8") as handle:
        records = list(csv.DictReader(handle))

    rows = []
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(fetch_record, record) for record in records]
        for future in as_completed(futures):
            rows.append(future.result())
            time.sleep(0.05)

    rows.sort(key=lambda row: (row.get("cluster", ""), str(row.get("id", ""))))

    safe_stamp = CAPTURED_AT.replace(":", "-")
    csv_path = LOG_DIR / f"zenodo_metrics_snapshot_watchlist_{safe_stamp}.csv"
    json_path = LOG_DIR / f"zenodo_metrics_snapshot_watchlist_{safe_stamp}.json"

    fieldnames = [
        "captured_at",
        "cluster",
        "notes",
        "id",
        "doi",
        "title",
        "resource_type",
        "publication_date",
        "version",
        "views",
        "unique_views",
        "downloads",
        "unique_downloads",
        "record_url",
        "status",
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Captured {len(rows)} records")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print()
    ok_rows = [row for row in rows if row["status"] == "ok"]
    ok_rows.sort(key=lambda row: int(row["views"] or 0), reverse=True)
    for row in ok_rows[:30]:
        print(f"{row['views']:>5} views {row['downloads']:>5} downloads | {row['cluster']} | {row['id']} | {row['title'][:90]}")

    errors = [row for row in rows if row["status"] != "ok"]
    if errors:
        print("\nErrors:")
        for row in errors:
            print(f"{row['id']}: {row['title']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
