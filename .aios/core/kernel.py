#!/usr/bin/env python3

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name, filename):
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / filename
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


services = load(
    "service_container",
    "service_container.py"
).services

event_bus = load(
    "event_bus",
    "event_bus.py"
).event_bus

config = load(
    "config_manager",
    "config_manager.py"
).config

logger = load(
    "logger",
    "logger.py"
).logger

permissions = load(
    "permission_manager",
    "permission_manager.py"
).permissions

scheduler = load(
    "task_scheduler",
    "task_scheduler.py"
).scheduler

memory = load(
    "memory_service",
    "memory_service.py"
).memory

knowledge = load(
    "knowledge_service",
    "knowledge_service.py"
).knowledge

llm = load(
    "llm_service",
    "llm_service.py"
).llm

lifecycle = load(
    "lifecycle",
    "lifecycle.py"
).lifecycle

runtime = load(
    "runtime",
    "runtime.py"
).runtime

hooks = load(
    "hooks",
    "hooks.py"
).hooks

pipeline = load(
    "pipeline",
    "pipeline.py"
).pipeline

router = load(
    "router",
    "router.py"
).router

command_bus = load(
    "command_bus",
    "command_bus.py"
).command_bus

query_bus = load(
    "query_bus",
    "query_bus.py"
).query_bus

event_store = load(
    "event_store",
    "event_store.py"
).event_store

state = load(
    "state_manager",
    "state_manager.py"
).state

registry = load(
    "module_registry",
    "module_registry.py"
).registry

health = load(
    "health_manager",
    "health_manager.py"
).health

resources = load(
    "resource_manager",
    "resource_manager.py"
).resources

metrics = load(
    "metrics",
    "metrics.py"
).metrics

manifest = load(
    "manifest_manager",
    "manifest_manager.py"
).manifest


CORE = {
    "event_bus": event_bus,
    "config": config,
    "logger": logger,
    "permissions": permissions,
    "scheduler": scheduler,
    "memory": memory,
    "knowledge": knowledge,
    "llm": llm,
    "lifecycle": lifecycle,
    "runtime": runtime,
    "hooks": hooks,
    "pipeline": pipeline,
    "router": router,
    "command_bus": command_bus,
    "query_bus": query_bus,
    "event_store": event_store,
    "state": state,
    "registry": registry,
    "health": health,
    "resources": resources,
    "metrics": metrics,
    "manifest": manifest,
}


for name, service in CORE.items():
    if not services.has(name):
        services.register(name, service)


if __name__ == "__main__":

    print()

    print("AIOS Kernel")

    print("-" * 40)

    for service in services.list():
        print(service)

    print("-" * 40)
    print(f"Services: {len(services.list())}")
