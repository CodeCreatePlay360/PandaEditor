# -*- coding: utf-8 -*-

"""
    Minimal Event system for python
"""

from .eventManager import EventManager, EventNotFound, HandlerNotFound

__all__ = ["Observable", "EventNotFound", "HandlerNotFound"]
