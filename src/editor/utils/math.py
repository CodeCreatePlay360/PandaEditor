
def map_to_range(old_min, old_max, new_min, new_max, value):
    """convert from one range to another"""
    old_range = old_max - old_min
    if old_range == 0:
        new_value = new_min
        return new_value
    else:
        new_range = new_max - new_min
        new_value = (((value - old_min) * new_range) / old_range) + new_min
        return new_value


def clamp(val, min_value, max_value):
    """clamps a value between min and max"""
    n = (val - min_value) / (max_value - min_value)
    return n


def clamp_angle(angle, min_val, max_val):
    """clamp angle to pi, -pi range"""
    if angle < -360:
        angle += 360
    if angle > 360:
        angle -= 360
    clamp = max(min(angle, max_val), min_val)
    return clamp

