import numpy as np

def convert_ndarrays_to_lists(obj):
    """
    Recursively converts all numpy arrays in a data structure to lists.
    """
    if isinstance(obj, dict):
        return {k: convert_ndarrays_to_lists(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_ndarrays_to_lists(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj
