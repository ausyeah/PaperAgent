import asyncio
import pytest
from paperagent.runner import StreamingSandboxRunner

@pytest.mark.asyncio
async def test_streaming_stdout():
    runner = StreamingSandboxRunner()
    code = "print('Hello'); print('World')"

    events = []
    async for event in runner.run_streaming(code):
        events.append(event)

    assert len(events) >= 4
    assert events[0]["event"] == "start"

    stdout_events = [e for e in events if e["event"] == "stdout"]
    assert len(stdout_events) == 2
    assert stdout_events[0]["data"] == "Hello"
    assert stdout_events[1]["data"] == "World"

    assert events[-1]["event"] == "done"
    assert events[-1]["exit_code"] == 0
    assert "duration_seconds" in events[-1]

@pytest.mark.asyncio
async def test_streaming_stderr():
    runner = StreamingSandboxRunner()
    code = "import sys; sys.stderr.write('Warn\\n')"

    events = []
    async for event in runner.run_streaming(code):
        events.append(event)

    stderr_events = [e for e in events if e["event"] == "stderr"]
    assert len(stderr_events) == 1
    assert stderr_events[0]["data"] == "Warn"

    assert events[-1]["event"] == "done"
    assert events[-1]["exit_code"] == 0

@pytest.mark.asyncio
async def test_streaming_timeout():
    runner = StreamingSandboxRunner()
    # Code that will definitely timeout
    code = "import time\nwhile True:\n    time.sleep(0.1)"

    events = []
    async for event in runner.run_streaming(code, timeout=0.5):
        events.append(event)

    assert events[-1]["event"] == "timeout"
    assert "error" in events[-1]

@pytest.mark.asyncio
async def test_streaming_cancellation():
    runner = StreamingSandboxRunner()
    code = "import time\nwhile True:\n    time.sleep(0.1)"

    events = []
    gen = runner.run_streaming(code, timeout=5.0)

    event = await gen.__anext__()
    assert event["event"] == "start"

    # Close the generator prematurely (this should trigger process kill in finally block)
    await gen.aclose()

    # Check that it doesn't leave orphaned processes
    # Because process.kill() is called in finally, there's no event yielded
    # but the process should be cleaned up.
