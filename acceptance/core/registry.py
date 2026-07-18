"""验收流程注册表：可扩展，未来别的流程在此登记。"""
from __future__ import annotations


REGISTRY: dict = {}


def register(name: str):
    """类装饰器：把流程类登记到 REGISTRY[name]。"""

    def deco(cls):
        REGISTRY[name] = cls
        return cls

    return deco


def get_flow(name: str):
    if name not in REGISTRY:
        raise KeyError(f"未知验收流程: {name}（已注册: {list(REGISTRY)}）")
    return REGISTRY[name]
