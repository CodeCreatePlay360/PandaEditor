
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
    _clamp = max(min(angle, max_val), min_val)
    return _clamp


def is_point_in_rect(rect, btm_left, btm_right, top_right, top_left):
    """determines if a point is inside rect"""
    # this is basically like drawing diagonals
    # x1 = point.x > BottomLeftCorner.x and point.x < TopRightCorner.x
    # x2 = point.z > BottomRightCorner.z and point.z < TopLeftCorner.z
    pass

