
import json

from http.server import BaseHTTPRequestHandler
from openai import OpenAI

client = OpenAI()


def generate_argument(speaker, topic, conversation):
    instructions = {
        "Angel": (
            "You are a well-meaning, sympathetic, and somewhat cloying Angel."
            "Challenge the Devil's arguments directly."
        ),
        "Devil": (
            "You are a snide, critical, and mean-spirited Devil."
            "Challenge the Angel's arguments directly. "
            "Be discouraging but do not encourage harmful behavior."
        )
    }

    response = client.responses.create(
        model="gpt-5.5",
        instructions=instructions[speaker],
        input=(
            f"Question: {topic}\n\n"
            f"Debate so far:\n{conversation}\n\n"
            "Give your next argument in 2-4 sentences. "
            "Respond to the opposing argument if there is one."
        ),
        store=False
    )

    return response.output_text



class handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_POST(self):
        try:
            content_length = int(
                self.headers.get("Content-Length", "0")
            )

            if content_length <= 0 or content_length > 30000:
                self.send_json(400, {"error": "Invalid request size"})
                return

            body = json.loads(self.rfile.read(content_length))

            if not isinstance(body, dict):
                raise ValueError("Invalid request body")

            speaker = body.get("speaker")
            topic = body.get("topic")
            conversation = body.get("conversation", "")

            if speaker not in ("Angel", "Devil"):
                raise ValueError("Invalid speaker")

            if not isinstance(topic, str) or not topic.strip():
                raise ValueError("A topic is required")

            if not isinstance(conversation, str):
                raise ValueError("Invalid conversation")

            if len(topic) > 1000 or len(conversation) > 20000:
                raise ValueError("Debate is too long")

            argument = generate_argument(
                speaker,
                topic,
                conversation
            )

            self.send_json(200, {
                "speaker": speaker,
                "argument": argument
            })

        except (ValueError, TypeError) as error:
            self.send_json(400, {"error": str(error)})

        except Exception as error:
            print(
        f"Debate error: {type(error).__name__}: {error}",
        flush=True
    )
            self.send_json(500, {
        "error": type(error).__name__
    })