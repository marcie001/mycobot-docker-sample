import os
import subprocess
import threading
from queue import Queue
from uuid import uuid4

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

tasks = Queue()

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])


class Task:
    def __init__(self, user, channel, image, respond, container=""):
        self.id = uuid4()
        self.user = user
        self.channel = channel
        self.image = image
        self.respond = respond
        self.container = container


@app.command("/mycobot")
def handle_mycobot_command(ack, respond, command):
    ack()
    args = command['text'].split()
    if len(args) == 0:
        respond("usage: /mycobot [docker image tag]")
    task = Task(command["user_id"], command["channel_id"], args[0], respond)
    tasks.put_nowait(task)
    respond(f"""Accepted
task ID: {task.id}
image: {task.image}
task queue length: {tasks.qsize()}""")


def run_container():
    while True:
        task = tasks.get()
        started = subprocess.run(
            ["docker", "container", "run", "-d", "--device", "/dev/ttyUSB0", task.image],
            capture_output=True,
            text=True,
        )
        if started.returncode != 0:
            task.respond(f"""failed to start container
exit code: {started.returncode}
stdout: {started.stdout}
stderr: {started.stderr}""")
            continue
        else:
            task.container = started.stdout.strip()
            task.respond(f"task ID: {task.id}\nstart container\ncontainer ID: {task.container}")

        waited = subprocess.run(
            ["docker", "container", "wait", task.container],
            capture_output=True,
            text=True,
        )
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
        task.respond(f"container exit code: {waited.stdout}\nlogs stdout: {logs.stdout}\nlogs stderr: {logs.stderr}")


if __name__ == "__main__":
    threading.Thread(target=run_container).start()
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
