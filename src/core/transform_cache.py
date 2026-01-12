"""
Transform Cache - Caches scaled and rotated sprites to avoid repeated transformations.
This provides significant performance improvements by reusing transformed surfaces.
"""

import pygame
from typing import Tuple, Optional


class TransformCache:
    """Cache transformed sprites with LRU eviction to manage memory"""

    def __init__(self, max_size: int = 500):
        """
        Initialize transform cache.

        Args:
            max_size: Maximum number of cached transformations
        """
        self.cache = {}
        self.max_size = max_size
        self.access_order = []  # Track access for LRU eviction

    def get_scaled(self, surface: pygame.Surface, size: Tuple[int, int]) -> pygame.Surface:
        """
        Get scaled surface from cache or create and cache it.

        Args:
            surface: Source surface to scale
            size: Target size (width, height)

        Returns:
            Scaled surface
        """
        key = (id(surface), 'scale', size)

        if key in self.cache:
            # Cache hit - move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]

        # Cache miss - transform and cache
        result = pygame.transform.scale(surface, size)
        self._add_to_cache(key, result)
        return result

    def get_rotated(self, surface: pygame.Surface, angle: float) -> pygame.Surface:
        """
        Get rotated surface from cache or create and cache it.
        Quantizes angle to 5-degree increments to improve cache hit rate.

        Args:
            surface: Source surface to rotate
            angle: Rotation angle in degrees

        Returns:
            Rotated surface
        """
        # Quantize angle to reduce cache misses (5-degree increments)
        angle = round(angle / 5) * 5
        key = (id(surface), 'rotate', angle)

        if key in self.cache:
            # Cache hit - move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]

        # Cache miss - transform and cache
        result = pygame.transform.rotate(surface, angle)
        self._add_to_cache(key, result)
        return result

    def get_flipped(self, surface: pygame.Surface, flip_x: bool, flip_y: bool) -> pygame.Surface:
        """
        Get flipped surface from cache or create and cache it.

        Args:
            surface: Source surface to flip
            flip_x: Whether to flip horizontally
            flip_y: Whether to flip vertically

        Returns:
            Flipped surface
        """
        key = (id(surface), 'flip', flip_x, flip_y)

        if key in self.cache:
            # Cache hit - move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]

        # Cache miss - transform and cache
        result = pygame.transform.flip(surface, flip_x, flip_y)
        self._add_to_cache(key, result)
        return result

    def _add_to_cache(self, key: tuple, surface: pygame.Surface):
        """
        Add surface to cache with LRU eviction.

        Args:
            key: Cache key
            surface: Surface to cache
        """
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]

        self.cache[key] = surface
        self.access_order.append(key)

    def clear(self):
        """Clear all cached transformations"""
        self.cache.clear()
        self.access_order.clear()

    def get_stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'utilization': len(self.cache) / self.max_size * 100
        }


# Global transform cache instance
_transform_cache = TransformCache(max_size=500)


def get_scaled(surface: pygame.Surface, size: Tuple[int, int]) -> pygame.Surface:
    """
    Get scaled surface from global cache.

    Args:
        surface: Source surface
        size: Target size (width, height)

    Returns:
        Scaled surface
    """
    return _transform_cache.get_scaled(surface, size)


def get_rotated(surface: pygame.Surface, angle: float) -> pygame.Surface:
    """
    Get rotated surface from global cache.

    Args:
        surface: Source surface
        angle: Rotation angle in degrees

    Returns:
        Rotated surface
    """
    return _transform_cache.get_rotated(surface, angle)


def get_flipped(surface: pygame.Surface, flip_x: bool, flip_y: bool) -> pygame.Surface:
    """
    Get flipped surface from global cache.

    Args:
        surface: Source surface
        flip_x: Flip horizontally
        flip_y: Flip vertically

    Returns:
        Flipped surface
    """
    return _transform_cache.get_flipped(surface, flip_x, flip_y)


def clear_cache():
    """Clear the global transform cache"""
    _transform_cache.clear()


def get_cache_stats() -> dict:
    """Get statistics from the global transform cache"""
    return _transform_cache.get_stats()
