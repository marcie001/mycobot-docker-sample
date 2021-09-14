import os
import subprocess

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Install the Slack app and get xoxb- token in advance
app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.command("/mycobot")
def handle_mycobot_command(ack, respond, command):
    ack()
    args = command['text'].split()
    if len(args) == 0:
        respond("usage: /mycobot [docker image tag]")
    complete = subprocess.run(
            ["docker", "container", "run", "-d", "--device", "/dev/ttyUSB0", args[0]],
            capture_output=True,
            text=True,
    )
    respond(f"exit status: {complete.returncode}\n--stdout--\n{complete.stdout}\n--stderr--\n{complete.stderr}\n")

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()

