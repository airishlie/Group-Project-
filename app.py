# Backend logic: receive messages, match keywords, save data, send replies
from flask import Flask, render_template, request, jsonify
import csv
from datetime import datetime
import os

app = Flask(__name__)

BOT_DATA_FILE = "bot_responses.csv"
LOG_FILE = "conversation_log.csv"


def load_bot_responses():
    responses = []

    with open(BOT_DATA_FILE, "r", newline="", encoding="utf-8-sig") as file:
        header_line = file.readline()
        detected_delimiter = ";" if ";" in header_line else ","

        file.seek(0)

        reader = csv.DictReader(file, delimiter=detected_delimiter)

        for row in reader:
            clean_row = {}
            for key, value in row.items():
                if key is not None:
                    clean_row[key.strip()] = value.strip() if value else ""
            responses.append(clean_row)

    return responses

def get_bot_reply(user_message):
    words = user_message.lower().strip().split()
    responses = load_bot_responses()

    for response in responses:
        keyword = response["keyword"].lower().strip()

        if keyword in words:
            return response["bot_reply"], keyword, "answered", "keyword matched"

    return (
        "Sorry, I do not have information about that yet.",
        "none",
        "unanswered",
        "no keyword matched"
    )


def get_next_conversation_no():
    if not os.path.exists(LOG_FILE):
        return 1

    with open(LOG_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        count = 0

        for row in reader:
            count += 1

    return count + 1


def save_conversation(username, user_message, matched_keyword, status, process, bot_reply):
    conversation_no = get_next_conversation_no()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:
        fieldnames = [
            "conversation_no",
            "username",
            "user_message",
            "matched_keyword",
            "status",
            "process",
            "bot_reply",
            "timestamp"
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "conversation_no": conversation_no,
            "username": username,
            "user_message": user_message,
            "matched_keyword": matched_keyword,
            "status": status,
            "process": process,
            "bot_reply": bot_reply,
            "timestamp": timestamp
        })


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    username = data.get("username", "").strip()
    user_message = data.get("message", "").strip()

    if username == "" or user_message == "":
        return jsonify({
            "error": "Username and message are required."
        }), 400

    bot_reply,matched_keyword,status,process = get_bot_reply(user_message)

    save_conversation(
        username,
        user_message,
        matched_keyword,
        status,
        process,
        bot_reply
    )

    return jsonify({
        "reply": bot_reply
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)
# run this in browser > http://127.0.0.1:5001