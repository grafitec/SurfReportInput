import json
import traceback
import os
from pathlib import Path
import xml.etree.ElementTree as ET

def tcx_to_json(tcx_path, rideId=''):
    try:
        TCX_NS = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
        NS = {"tcx": TCX_NS}
        tcx_file = Path(tcx_path)
        if os.path.exists(tcx_file):
            root = ET.parse(tcx_file).getroot()

            points = []
            index = 0
            for point in root.findall(".//tcx:Trackpoint", NS):
                time_el = point.find("tcx:Time", NS)
                lat_el = point.find("tcx:Position/tcx:LatitudeDegrees", NS)
                lon_el = point.find("tcx:Position/tcx:LongitudeDegrees", NS)

                if time_el is None or time_el.text is None:
                    continue
                if lat_el is None or lon_el is None:
                    continue

                points.append({
                    "id": float(1),
                    "index": int(index),
                    "time": time_el.text,
                    "latitude": float(lat_el.text),
                    "longitude": float(lon_el.text),

                })
                index = index + 1
            if rideId == '':
                untrackedVersion = str(tcx_path).split('.')[0].split('_')[-1]
                json_filename = f"appleWatchRideData_rideId_{untrackedVersion}.json"
            else:
                json_filename = f"appleWatchRideData_rideId_{rideId}.json"
            json_folder = (
                    Path(__file__).parent.parent.parent
                    / "data"
                    / "json"
            )
            json_folder.mkdir(parents=True, exist_ok=True)
            json_path = (Path(json_folder) / json_filename)
            json_file = Path(json_path)
            with json_file.open("w", encoding="utf-8") as f:
                json.dump(points, f, indent=2, ensure_ascii=False)
            path = str(json_file).replace('\\', '/')
            return path
        else:
            return None
    except Exception:
        traceback.print_exc()