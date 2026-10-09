
import os
import ssl
import smtplib
from email.message import EmailMessage

from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# The address that receives her answers
RECIPIENT_EMAIL = "tomasmatkovic@gmail.com"

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>A little question for you</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    font-family: Arial, sans-serif;
    background: linear-gradient(135deg, #ccd2ff, #d2ccff, #ccd2ff);
    color: #663322;
}

.card {
    width: 100%;
    max-width: 500px;
    padding: 30px 24px;
    background: white;
    border-radius: 26px;
    text-align: center;
    box-shadow: 0 15px 50px #a0325a30;
}

.heart {
    font-size: 60px;
    animation: beat 1.2s infinite;
}

@keyframes beat {
    50% { transform: scale(1.12); }
}

h1 { font-size: clamp(25px, 6vw, 35px); }
p { line-height: 1.6; }

button {
    padding: 14px 22px;
    border: none;
    border-radius: 14px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
}

.buttons {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 30px;
    min-height: 55px;
}

#yes, #send {
    background: #ddc2ff;
    color: white;
}

#no {
    background: #eee;
    color: #555;
}

.hidden { display: none; }

.choices {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 24px 0;
}

.choice {
    background: #fff0f5;
    border: 2px solid transparent;
}

.choice.selected {
    border-color: #ff6392;
    background: #ffe0eb;
}

input, textarea {
    display: block;
    width: 100%;
    padding: 13px;
    margin: 8px 0 18px;
    border: 1px solid #efc3d1;
    border-radius: 12px;
    font: inherit;
}

textarea { min-height: 80px; }

#send { width: 100%; }

.small {
    color: #997382;
    font-size: 13px;
}

#message {
    overflow-wrap: anywhere;
    margin-top: 16px;
}
</style>
</head>

<body>
<div class="card">

<section id="question">
    <div class="heart"></div>
    <h1>Will you go out with me?</h1>
    <p>I have a little question for you...</p>

    <div class="buttons">
        <button id="yes" onclick="showNext()">Yes! 🫶</button>
       <button id="no">No 🥺</button>
</div>

<p class="small" id="hint">Choose wisely 🤔</p>
</section>

<section id="next" class="hidden">
    <div class="heart"></div>
    <h1>Nice! I was hoping you'd say yes!</h1>

    <p>
        When you're free, choose what kind of activity
        you'd like to do. We can figure out the details together.
    </p>

    <div class="choices">
        <button class="choice" onclick="choose(this, 'Coffee')">
            ☕ Coffee/🐈 Cat café
        </button>
        <button class="choice" onclick="choose(this, 'A walk')">
            🌅 A walk
        </button>
        <button class="choice" onclick="choose(this, 'Bowling')">
            🎳 Bowling
        </button>
        <button class="choice" onclick="choose(this, 'Zoo')">
            🦒 Zoo
        </button>
        <button class="choice" onclick="choose(this, 'Cinema')">
            🎬 Cinema
        </button>
        <button class="choice" onclick="choose(this, 'Surprise me')">
            🎁 Surprise me
        </button>
    </div>

    <label for="when">When are you free?</label>
    <input id="when" maxlength="300"
           placeholder="e.g. Friday afternoon">

    <label for="other">Any other ideas? (optional)</label>
    <textarea id="other" maxlength="2000"
              placeholder="Tell me your ideas..."></textarea>

    <button id="send" onclick="sendResponse()">
        Sounds good! 
    </button>

    <div id="message" role="status"></div>
</section>

</div>

<script>
const noButton = document.getElementById("no");
let selectedActivity = "";

function escapeNo(event) {
    const width = noButton.offsetWidth;
    const height = noButton.offsetHeight;

    const maxX = Math.max(5, window.innerWidth - width - 5);
    const maxY = Math.max(5, window.innerHeight - height - 5);

    let x = 5;
    let y = 5;

    for (let i = 0; i < 30; i++) {
        x = 5 + Math.random() * Math.max(0, maxX - 5);
        y = 5 + Math.random() * Math.max(0, maxY - 5);

        if (Math.hypot(
            x + width / 2 - event.clientX,
            y + height / 2 - event.clientY
        ) > 150) break;
    }

    noButton.style.position = "fixed";
    noButton.style.left = x + "px";
    noButton.style.top = y + "px";

    document.getElementById("hint").textContent =
        "Haha, not so easy! 😂";
}

noButton.addEventListener("pointerenter", escapeNo);

noButton.addEventListener("touchstart", function(event) {
    event.preventDefault();

    const maxX = Math.max(0, window.innerWidth - noButton.offsetWidth);
    const maxY = Math.max(0, window.innerHeight - noButton.offsetHeight);

    noButton.style.position = "fixed";
    noButton.style.left = Math.random() * maxX + "px";
    noButton.style.top = Math.random() * maxY + "px";
}, { passive: false });

function showNext() {
    document.getElementById("question").classList.add("hidden");
    document.getElementById("next").classList.remove("hidden");
    document.body.style.alignItems = "flex-start";
}

function choose(button, activity) {
    selectedActivity = activity;

    document.querySelectorAll(".choice").forEach(item => {
        item.classList.remove("selected");
    });

    button.classList.add("selected");
}

async function sendResponse() {
    const sendButton = document.getElementById("send");
    const message = document.getElementById("message");

    sendButton.disabled = true;
    sendButton.textContent = "Sending... ";
    message.textContent = "";

    const data = {
        activity: selectedActivity || "Let's decide together",
        when: document.getElementById("when").value.trim(),
        other: document.getElementById("other").value.trim()
    };

    try {
        const response = await fetch("/send-response", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Could not send the response.");
        }

        message.textContent =
            "Sent successfully! Thank you " ;
        sendButton.textContent = "Sent! " ;

    } catch (error) {
        message.textContent =
            "Sorry, the response could not be sent. " + error.message;

        sendButton.disabled = false;
        sendButton.textContent = "Try again";
    }
}
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/send-response", methods=["POST"])
def send_response():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="Invalid response data."), 400

    activity = str(data.get("activity", "Let's decide together"))[:300]
    when = str(data.get("when", ""))[:300]
    other = str(data.get("other", ""))[:2000]

    # These values are set in the terminal, not saved in this file.
    sender_email = os.environ.get("GMAIL_ADDRESS", "").strip()
    app_password = os.environ.get("GMAIL_APP_PASSWORD", "").replace(" ", "")
    print("GMAIL_ADDRESS configured:", bool(sender_email))
    print("GMAIL_APP_PASSWORD configured:", bool(app_password))
    if not sender_email or not app_password:
        app.logger.error("Gmail environment variables are not configured.")
        return jsonify(
            error="Email is not configured. Ask the website owner to check the Gmail settings."
        ), 500

    email = EmailMessage()
    email["Subject"] = "❤️ New answer to your date invitation!"
    email["From"] = sender_email
    email["To"] = RECIPIENT_EMAIL

    email.set_content(
        "Someone answered your date invitation!\n\n"
        f"Activity: {activity}\n"
        f"When: {when or 'Not specified'}\n"
        f"Other ideas: {other or 'None'}\n\n"
        "Sent by your date invitation website."
    )

    try:
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(
            "smtp.gmail.com", 465, context=context, timeout=20
        ) as server:
            server.login(sender_email, app_password)
            server.send_message(email)

        app.logger.info("Date invitation response email sent.")
        return jsonify(success=True)

    except (smtplib.SMTPException, OSError, TimeoutError):
        app.logger.exception("Email delivery failed.")
        return jsonify(
            error="Email delivery failed. Check the Gmail settings and try again."
        ), 500


if __name__ == "__main__":
    app.run(debug=True)
