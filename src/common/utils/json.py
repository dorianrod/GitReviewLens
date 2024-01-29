import json
from dataclasses import asdict
from json import JSONEncoder


def recursive_asdict(obj, first_level=True):
    if not first_level and hasattr(obj, "to_dict"):
        return obj.to_dict()

    base = obj
    try:
        base = asdict(
            obj,
        )
        for key in base:
            try:
                if hasattr(getattr(obj, key), "to_dict"):
                    base[key] = recursive_asdict(getattr(obj, key), False)
                if isinstance(getattr(obj, key), list):
                    base[key] = [
                        recursive_asdict(item, False) for item in getattr(obj, key)
                    ]
            except Exception:
                pass
    except Exception:
        pass
    finally:
        return base


class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        try:
            return o.to_dict()
        except Exception:
            return super().default(o)


def jsonify(data):
    return json.dumps(data, cls=CustomJSONEncoder)
