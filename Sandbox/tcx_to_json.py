#!/usr/bin/env python3

import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

TCX_NS = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
NS = {"tcx": TCX_NS}


def tcx_to_json(tcx_path: str, json_path: str | None = None) -> Path:
    tcx_file = Path(tcx_path)

    if not tcx_file.exists():
        raise FileNotFoundError(f"Filen finns inte: {tcx_file}")

    root = ET.parse(tcx_file).getroot()

    points = []

    # Läs ALLA Trackpoint från hela aktiviteten.
    # Laps ignoreras helt.
    for point in root.findall(".//tcx:Trackpoint", NS):
        time_el = point.find("tcx:Time", NS)
        lat_el = point.find("tcx:Position/tcx:LatitudeDegrees", NS)
        lon_el = point.find("tcx:Position/tcx:LongitudeDegrees", NS)

        # Hoppa över punkter som saknar tid eller GPS-position.
        if time_el is None or time_el.text is None:
            continue
        if lat_el is None or lon_el is None:
            continue

        points.append({
            "time": time_el.text,
            "latitude": float(lat_el.text),
            "longitude": float(lon_el.text),
        })

    if not points:
        raise ValueError("Hittade inga Trackpoints med både tid och GPS-position.")

    # Om ingen outputfil anges: använd samma namn som TCX-filen, men .json
    if json_path is None:
        json_file = tcx_file.with_suffix(".json")
    else:
        json_file = Path(json_path)

    with json_file.open("w", encoding="utf-8") as f:
        json.dump(points, f, indent=2, ensure_ascii=False)

    return json_file


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Användning:")
        print('  python tcx_to_json.py "min_traning.tcx"')
        print('  python tcx_to_json.py "min_traning.tcx" "min_traning.json"')
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) == 3 else None

    try:
        result = tcx_to_json(input_file, output_file)
        print(f"Klart! Skrev JSON till: {result}")
    except Exception as e:
        print(f"Fel: {e}")
        sys.exit(1)
