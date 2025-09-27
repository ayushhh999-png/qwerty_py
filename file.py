from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory
import json
import os
from datetime import datetime
from threading import Lock

app = Flask(__name__)
DATA_FILE = "results.json"
lock = Lock()

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# Main page: shows prompt and last result summary
@app.route("/", methods=["GET"])
def index():
    with open(DATA_FILE, "r") as f:
        results = json.load(f)
    last = results[-1] if results else None

    template = r"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>will you go on a date?</title>
      <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
      <style>
        :root{--pink:#ffadcc;--deep:#3a2b5b}
        body{margin:0;font-family:Inter,system-ui,Arial;background:linear-gradient(135deg,#ffd6e0 0%, #fff 40%, #fceef5 100%);min-height:100vh;display:flex;align-items:center;justify-content:center}
        .card{width:92%;max-width:720px;background:rgba(255,255,255,0.72);backdrop-filter:blur(6px);border-radius:20px;padding:28px;box-shadow:0 8px 30px rgba(58,43,91,0.12)}
        h1{font-family:'Great Vibes',cursive;font-size:46px;color:var(--deep);margin:0 0 8px}
        p.lead{margin:0 0 18px;color:#5b3f66}
        .hero{display:flex;gap:18px;align-items:center}
        .hero img{width:180px;height:120px;object-fit:cover;border-radius:12px;box-shadow:0 6px 18px rgba(0,0,0,0.08)}
        .buttons{margin-top:16px}
        .btn{padding:12px 20px;border-radius:999px;border:none;font-weight:600;margin-right:10px;cursor:pointer}
        .yes{background:linear-gradient(90deg,#ff8ab8,#ff5f8a);color:white}
        .no{background:transparent;border:2px solid #ff8ab8;color:var(--deep)}
        .result{margin-top:18px;padding:14px;border-radius:12px;background:linear-gradient(90deg,rgba(255,250,245,0.9),rgba(255,245,255,0.9));box-shadow:inset 0 1px 0 rgba(255,255,255,0.6)}
        .small{font-size:13px;color:#6b5b6b}
        .history{margin-top:12px}
        .emoji{font-size:20px;margin-left:8px}
      </style>
    </head>
    <body>
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <h1>you wanna go on a date with me?</h1>
          </div>
          <div class="small">Saved results appear below</div>
        </div>

        <div class="hero">
          <img src="https://assets.newsweek.com/wp-content/uploads/2025/08/2188745-kim-ngan-le-ginger-cat-01-banner.jpg?w=1360&quality=75&webp=1" alt="cat">
          <div style="flex:1">
            <form method="post" action="/choose">
              <input type="hidden" name="step" value="initial">
              <div class="buttons">
                <button class="btn yes" name="choice" value="yes">Yes</button>
                <button class="btn no" name="choice" value="no">No</button>
              </div>
            </form>
            <div class="small" style="margin-top:10px">(Your choice will be saved)</div>
          </div>
        </div>

        {% if last %}
        <div class="history">
          <div class="small">Latest response:</div>
          <div class="result">{{ last.display }} <span class="emoji">{{ last.emoji }}</span>
            <div class="small" style="margin-top:6px">Completed at: {{ last.time }}</div>
          </div>
        </div>
        {% endif %}

      </div>

      <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    </body>
    </html>
    """

    return render_template_string(template, last=last)


# Handle choices and flow
@app.route("/choose", methods=["POST"])
def choose():
    step = request.form.get("step")
    choice = request.form.get("choice")

    # initial step: yes/no
    if step == "initial":
        if choice == "yes":
            display = "thanks Mrs. Shrestha, now you are legally obliged to be spoiled by ayushi without any recessions."
            emoji = "🎉"
            save_result({"time":datetime.utcnow().isoformat(), "flow":"initial", "choice":"yes", "display":display, "emoji":emoji})
            return render_thanks(display, emoji)
        else:
            # show heartbreak page with second choice
            return render_no_page()

    # second step when user clicked no previously
    if step == "second":
        if choice == "yes":
            display = "ayushi will cry himself to sleep"
            emoji = "😢"
            save_result({"time":datetime.utcnow().isoformat(), "flow":"no->yes", "choice":"yes", "display":display, "emoji":emoji})
            return render_final(display, emoji)
        else:
            display = "please give ayushi a chanceeee he is a good guy"
            emoji = "🙏"
            save_result({"time":datetime.utcnow().isoformat(), "flow":"no->no", "choice":"no", "display":display, "emoji":emoji})
            return render_final(display, emoji)

    # fallback redirect
    return redirect(url_for('index'))


def render_thanks(message, emoji):
    # Greeting animation + confetti
    template = r"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>thanks!</title>
      <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
      <style>
        body{display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:linear-gradient(135deg,#fff0f6,#fff8f2)}
        .box{background:white;padding:28px;border-radius:16px;box-shadow:0 10px 30px rgba(0,0,0,0.08);text-align:center}
        h2{font-family:'Great Vibes',cursive;font-size:40px;margin:0;color:#b02e6a}
        p{color:#5b3f66}
      </style>
    </head>
    <body>
      <div class="box">
        <h2>{{ message }}</h2>
        <p style="margin-top:12px">{{ emoji }}</p>
      </div>

      <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
      <script>
        // simple confetti burst
        function burst(){
          confetti({particleCount:120, spread:140, origin:{y:0.6}});
        }
        // animate greeting: several bursts
        burst();
        setTimeout(burst, 600);
        setTimeout(burst, 1200);
      </script>
    </body>
    </html>
    """
    return render_template_string(template, message=message, emoji=emoji)


def render_no_page():
    template = r"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>oh no...</title>
      <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
      <style>
        body{display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:linear-gradient(135deg,#fff6f8,#fffefc)}
        .box{background:white;padding:20px;border-radius:12px;max-width:720px;box-shadow:0 8px 22px rgba(0,0,0,0.06);display:flex;gap:16px}
        .box img{width:200px;height:140px;object-fit:cover;border-radius:10px}
        .content{flex:1}
        .btn{padding:10px 16px;border-radius:999px;border:none;font-weight:600;margin-right:10px;cursor:pointer}
        .yes{background:linear-gradient(90deg,#ff8ab8,#ff5f8a);color:white}
        .no{background:transparent;border:2px solid #ff8ab8;color:#5b3f66}
      </style>
    </head>
    <body>
      <div class="box">
        <img src="https://external-preview.redd.it/RpCJRcnrVAqT38N-1nQEB2xGaDxoBaNSy7DDginPRFI.jpg?width=640&crop=smart&auto=webp&s=418db22ccbe2cf85c27e1e6f0164d8ec75118649" alt="sad">
        <div class="content">
          <h3 style="margin:0">you really gonna break his heart? 🥺</h3>
          <p class="small">(one more question)</p>
          <form method="post" action="/choose">
            <input type="hidden" name="step" value="second">
            <div style="margin-top:12px">
              <button class="btn yes" name="choice" value="yes">Yes</button>
              <button class="btn no" name="choice" value="no">No</button>
            </div>
          </form>
        </div>
      </div>
    </body>
    </html>
    """
    return render_template_string(template)


def render_final(message, emoji):
    template = r"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>final</title>
      <style>body{font-family:Inter,Arial;margin:0;display:flex;align-items:center;justify-content:center;min-height:100vh;background:linear-gradient(135deg,#fff7f9,#fff)}.card{background:white;padding:28px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.06);text-align:center}</style>
    </head>
    <body>
      <div class="card">
        <h3>{{ message }}</h3>
        <div style="margin-top:12px">{{ emoji }}</div>
        <div style="margin-top:14px"><a href="/">Back to main</a></div>
      </div>
    </body>
    </html>
    """
    return render_template_string(template, message=message, emoji=emoji)


def save_result(data):
    # append to JSON file safely
    with lock:
        with open(DATA_FILE, "r+") as f:
            try:
                arr = json.load(f)
            except Exception:
                arr = []
            arr.append(data)
            f.seek(0)
            json.dump(arr, f, indent=2)
            f.truncate()


if __name__ == '__main__':
    app.run(debug=True)
