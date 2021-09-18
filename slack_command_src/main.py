import os
import subprocess
import signal
import threading
from queue import Queue
from uuid import uuid4

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()
tasks = Queue()

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])


class Task:
    def __init__(self, image="", respond="", container="", done=False, cleanup=False):
        self.id = uuid4()
        self.image = image
        self.respond = respond
        self.container = container
        self.done = done
        self.cleanup = cleanup


@app.command("/mycobot")
def handle_mycobot_command(ack, respond, command):
    ack()
    args = command['text'].split()
    if len(args) == 0:
        respond({
            "response_type": "in_channel",
            "text": "usage: /mycobot [docker image tag]",
        })
    task = Task(image=args[0], respond=respond)
    tasks.put_nowait(task)
    text = f"""Accepted
task ID: {task.id}
image: {task.image}
task queue length: {tasks.qsize()}"""
    respond({
        "response_type": "in_channel",
        "text": text,
    })


def kill_container_func(task):
    def f():
        if task.done:
            return
        killed = subprocess.run(
            ["docker", "container", "wait", task.container],
            capture_output=True,
            text=True,
        )
        if killed.returncode != 0:
            if "No such container:" not in killed.stderr:
                task.respond({
                    "response_type": "in_channel",
                    "text": f"failed to kill a container: {task.container}\n{killed.stderr}",
                })

    return f


def run_container():
    while True:
        task = tasks.get()
        if task.cleanup:
            print("exit run_container")
            return
        started = subprocess.run(
            ["docker", "container", "run", "-d", "--device", "/dev/ttyUSB0", task.image],
            capture_output=True,
            text=True,
        )
        if started.returncode != 0:
            text = f"""failed to start container
exit code: {started.returncode}
stdout: {started.stdout}
stderr: {started.stderr}"""
            task.respond({
                "response_type": "in_channel",
                "text": text,
            })
            continue
        else:
            task.container = started.stdout.strip()
            task.respond({
                "response_type": "in_channel",
                "text": f"task ID: {task.id}\nstart container\ncontainer ID: {task.container}",
            })

        f = kill_container_func(task)
        threading.Timer(180.0, f).start()

        waited = subprocess.run(
            ["docker", "container", "wait", task.container],
            capture_output=True,
            text=True,
        )
        task.done = True
        logs = subprocess.run(
            ["docker", "container", "logs", task.container],
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["docker", "container", "rm", task.container],
            capture_output=True,
            text=True,
        )
        text = f"container exit code: {waited.stdout.strip()}\nlogs stdout: {logs.stdout}\nlogs stderr: {logs.stderr}"
        task.respond({
            "response_type": "in_channel",
            "text": text,
        })


def cleanup_func(socket_mode_handler):
    def f(signum, frame):
        print("cleanup")
        socket_mode_handler.close()
        tasks.put_nowait(Task(cleanup=True))

    return f


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.connect()
    c = cleanup_func(handler)
    signal.signal(signal.SIGINT, c)
    signal.signal(signal.SIGTERM, c)

    run_container()
