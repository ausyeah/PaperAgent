import asyncio
import sys
import time
import tempfile
from pathlib import Path
from typing import AsyncGenerator

class StreamingSandboxRunner:
    """Safely executes generated Python code in a subprocess and streams output."""

    async def run_streaming(self, code: str, timeout: float = 30.0) -> AsyncGenerator[dict, None]:
        """
        Executes Python code in an isolated temporary directory.
        Streams stdout and stderr line by line.
        """
        start_time = time.time()
        yield {"event": "start", "timestamp": start_time}

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            target_file = temp_dir / "run_target.py"
            target_file.write_text(code, encoding="utf-8")

            process = await asyncio.create_subprocess_exec(
                sys.executable, str(target_file),
                cwd=str(temp_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            async def read_stream(stream, event_name, queue):
                while True:
                    line = await stream.readline()
                    if not line:
                        break
                    decoded_line = line.decode('utf-8', errors='replace').rstrip('\r\n')
                    await queue.put({"event": event_name, "data": decoded_line})
                await queue.put(None)

            queue = asyncio.Queue()

            stdout_task = asyncio.create_task(read_stream(process.stdout, "stdout", queue))
            stderr_task = asyncio.create_task(read_stream(process.stderr, "stderr", queue))

            streams_completed = 0

            try:
                # We use a timeout for the entire execution
                # wait_for would apply to the process.wait(), but we need to yield from the queue.
                # So we can calculate time remaining and wait for the queue.

                while streams_completed < 2:
                    elapsed = time.time() - start_time
                    time_left = timeout - elapsed

                    if time_left <= 0:
                        raise asyncio.TimeoutError()

                    # Wait for next item in the queue with a timeout
                    item = await asyncio.wait_for(queue.get(), timeout=time_left)

                    if item is None:
                        streams_completed += 1
                    else:
                        yield item

                # Wait for process to exit to get return code
                elapsed = time.time() - start_time
                time_left = timeout - elapsed
                if time_left <= 0:
                    raise asyncio.TimeoutError()

                await asyncio.wait_for(process.wait(), timeout=time_left)

                duration = time.time() - start_time
                yield {"event": "done", "exit_code": process.returncode, "duration_seconds": duration}

            except asyncio.TimeoutError:
                yield {"event": "timeout", "error": "Execution timed out"}
            except asyncio.CancelledError:
                # E.g. generator closed
                raise
            finally:
                if process.returncode is None:
                    try:
                        process.kill()
                        await process.wait()
                    except (ProcessLookupError, Exception):
                        pass

                stdout_task.cancel()
                stderr_task.cancel()

