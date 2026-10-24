"""Shared agent package setup.

Python 3.14 no longer creates an event loop implicitly. uAgents 0.25.5 asks for the current loop
inside Agent(...), which then raises "There is no current event loop in thread 'MainThread'".
Make sure a loop exists before any agent module builds its Agent. This runs for every
`python -m agents.<name>` because the package is imported first.
"""
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
