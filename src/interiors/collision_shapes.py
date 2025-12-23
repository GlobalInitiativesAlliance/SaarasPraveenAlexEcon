"""
Professional Collision Shape System

Uses simple geometric primitives (circles, rectangles) for efficient,
smooth collision detection - the industry standard approach.

Circle math is O(1), rectangle is simple AABB - both run at 60fps easily.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import math


class ShapeType(Enum):
    """Types of collision shapes."""
    CIRCLE = "circle"
    RECTANGLE = "rect"


@dataclass
class CollisionShape:
    """
    A collision shape primitive.

    For CIRCLE: x, y = center position, width = radius (height unused)
    For RECTANGLE: x, y = top-left corner, width/height = dimensions
    """
    shape_type: ShapeType
    x: float
    y: float
    width: float = 0   # radius for circles, width for rects
    height: float = 0  # unused for circles


def circle_vs_circle(c1: CollisionShape, c2: CollisionShape) -> bool:
    """
    Check collision between two circles.
    O(1) - just one distance comparison.

    Args:
        c1: First circle (x, y = center, width = radius)
        c2: Second circle

    Returns:
        True if circles overlap
    """
    dx = c1.x - c2.x
    dy = c1.y - c2.y
    dist_sq = dx * dx + dy * dy
    radius_sum = c1.width + c2.width
    return dist_sq < radius_sum * radius_sum


def circle_vs_rect(circle: CollisionShape, rect: CollisionShape) -> bool:
    """
    Check collision between a circle and a rectangle.
    Finds the closest point on the rect to the circle center.

    Args:
        circle: Circle shape (x, y = center, width = radius)
        rect: Rectangle shape (x, y = top-left, width/height = size)

    Returns:
        True if circle overlaps rectangle
    """
    # Find closest point on rectangle to circle center
    closest_x = max(rect.x, min(circle.x, rect.x + rect.width))
    closest_y = max(rect.y, min(circle.y, rect.y + rect.height))

    # Check if closest point is within circle radius
    dx = circle.x - closest_x
    dy = circle.y - closest_y
    dist_sq = dx * dx + dy * dy

    return dist_sq < (circle.width * circle.width)


def rect_vs_rect(r1: CollisionShape, r2: CollisionShape) -> bool:
    """
    Check collision between two rectangles (AABB).
    Simple overlap check.

    Args:
        r1: First rectangle
        r2: Second rectangle

    Returns:
        True if rectangles overlap
    """
    return (r1.x < r2.x + r2.width and
            r1.x + r1.width > r2.x and
            r1.y < r2.y + r2.height and
            r1.y + r1.height > r2.y)


def check_collision(shape1: CollisionShape, shape2: CollisionShape) -> bool:
    """
    Universal collision check between any two shapes.

    Args:
        shape1: First collision shape
        shape2: Second collision shape

    Returns:
        True if shapes collide
    """
    if shape1.shape_type == ShapeType.CIRCLE:
        if shape2.shape_type == ShapeType.CIRCLE:
            return circle_vs_circle(shape1, shape2)
        else:
            return circle_vs_rect(shape1, shape2)
    else:
        if shape2.shape_type == ShapeType.CIRCLE:
            return circle_vs_rect(shape2, shape1)
        else:
            return rect_vs_rect(shape1, shape2)


def get_circle_penetration(c1: CollisionShape, c2: CollisionShape) -> Optional[tuple]:
    """
    Get the penetration vector to push c1 out of c2.
    Useful for smooth sliding along surfaces.

    Args:
        c1: First circle (the one to push out)
        c2: Second circle (stationary)

    Returns:
        (push_x, push_y) to separate circles, or None if no collision
    """
    dx = c1.x - c2.x
    dy = c1.y - c2.y
    dist_sq = dx * dx + dy * dy
    radius_sum = c1.width + c2.width

    if dist_sq >= radius_sum * radius_sum:
        return None  # No collision

    dist = math.sqrt(dist_sq)
    if dist == 0:
        # Circles at same position, push in arbitrary direction
        return (radius_sum, 0)

    # Normalize and scale by penetration depth
    penetration = radius_sum - dist
    return (dx / dist * penetration, dy / dist * penetration)


def get_circle_rect_penetration(circle: CollisionShape, rect: CollisionShape) -> Optional[tuple]:
    """
    Get the penetration vector to push circle out of rectangle.

    Args:
        circle: Circle shape
        rect: Rectangle shape

    Returns:
        (push_x, push_y) to separate shapes, or None if no collision
    """
    # Find closest point on rectangle to circle center
    closest_x = max(rect.x, min(circle.x, rect.x + rect.width))
    closest_y = max(rect.y, min(circle.y, rect.y + rect.height))

    dx = circle.x - closest_x
    dy = circle.y - closest_y
    dist_sq = dx * dx + dy * dy

    if dist_sq >= circle.width * circle.width:
        return None  # No collision

    dist = math.sqrt(dist_sq)
    if dist == 0:
        # Circle center inside rect, push to nearest edge
        left = circle.x - rect.x
        right = rect.x + rect.width - circle.x
        top = circle.y - rect.y
        bottom = rect.y + rect.height - circle.y

        min_dist = min(left, right, top, bottom)
        if min_dist == left:
            return (-circle.width - left, 0)
        elif min_dist == right:
            return (circle.width + right, 0)
        elif min_dist == top:
            return (0, -circle.width - top)
        else:
            return (0, circle.width + bottom)

    # Push circle out along the collision normal
    penetration = circle.width - dist
    return (dx / dist * penetration, dy / dist * penetration)
