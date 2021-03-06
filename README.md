# AIO Task Bound Context
Context manager that provides a means for context to be set, and retrieved
in Python AsyncIO.

## What???
Okay so for a concrete example, thing of how Flask handles the current request:

```python
from flask import request
```

This import, called from anywhere, will import the current request being
handled. This is made possible in a way similar to this:

```python
request = None
def get_request():
    return request
def set_request(value):
    global request
    request = value
```

When the HTTP server gets a request, it will call `set_request`, then anywhere
in the code another function can call `get_request` to get the value.

Here's the kicker: This is not possible with AIO, because multiple tasks may
be running at once, so there are multiple values for `request`, rather than
just a single value. Imagine the same piece of code being used in AIO:

```python
import asyncio as aio

async def handle_request(request):
    set_request(request)
    # generate the response
    await aio.sleep(1)
    assert get_request() == request  # will fail
    set_request(None)

aio.get_event_loop().run_until_complete(aio.gather(
    handle_request('value 1'),
    handle_request('value 2'),
))
```

Obviously, this is going to be problematic.

## The answer
`aio_task_bound_context` attaches a stack of the current context values to the
current `Task`, as well as tracking the parent tasks so that their context
can be inherrited:

```python
import asyncio as aio
from aio_task_bound_context import TaskBoundContext

class RequestContext(TaskBoundContext):
    def __init__(self, request):
        self.request = request
    def get_value(self):
        return self.request

async def handle_request(request):
    with RequestContext(request):
        # generate the response
        await aio.sleep(1)
        assert RequestContext.current() == request # will succeed

aio.get_event_loop().run_until_complete(aio.gather(
    handle_request('value 1'),
    handle_request('value 2'),
))
```

## Testing
Python 3.5+ is supported. To run tests across all environments, we use
`pyenv`, and some quick `virtualenv` invocations (yes, we could also use
`tox`).

To run the tests, just run `./tests_runall.sh` which will install relevant
Python versions if not already installed, create virtualenvs for them, and
run `tests.py`.

To run tests manually, simply `./test.py`.

## License
Copyright 2018 Ricky Cook

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
