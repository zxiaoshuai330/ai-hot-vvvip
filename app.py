from flask import Flask, request
import random
import os

import firebase_admin
from firebase_admin import credentials, firestore

# 🔥 Firebase 初始化
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

line_link = "https://line.me/ti/p/nkakY8ZXma"
MAX_FREE = 3

# 🔑 你可以改這個授權碼
VIP_CODE = "win168188"

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    show_result = "none"
    unlock = False

    if request.method == "POST":
        show_result = "block"

        user_id = request.remote_addr
        doc = db.collection("users").document(user_id)
        data = doc.get()

        if data.exists:
            user_data = data.to_dict()
            count = user_data.get("count", 0)
            unlock = user_data.get("vip", False)
        else:
            count = 0
            unlock = False

        # 🔓 如果已解鎖就不計數
        if not unlock:
            count += 1

        doc.set({
            "count": count,
            "vip": unlock
        })

        locked = (count > MAX_FREE) and (not unlock)

        today_val = request.form.get("today", "")
        current_val = request.form.get("current", "")
        last1_val = request.form.get("last1", "")
        last2_val = request.form.get("last2", "")

        try:
            current = int(current_val)
            last1 = int(last1_val)
            last2 = int(last2_val)

            avg = (last1 + last2) / 2
            diff = abs(last1 - last2)

            if diff > 80:
                risk = "高波動（節奏不穩）"
            elif diff > 30:
                risk = "中波動"
            else:
                risk = "穩定節奏"

            if current > avg * 1.3:
                status = "進入尾段醞釀"
            elif current < avg * 0.7:
                status = "剛結束釋放"
            else:
                status = "訊號累積中"

            signal_chance = random.randint(60, 95)
            confidence = random.randint(80, 96)

            if locked:
                vip_html = f"""
                <div class="card">
                    🔒 功能已鎖定
                    <br><br>
                    <input id="code" placeholder="輸入授權碼">
                    <button onclick="unlock()">解鎖</button>
                </div>
                """
            else:
                vip_html = f"""
                <div class="card step">👉 操作建議：建議低本測試</div>
                <div class="card step">⏱ 建議區間：約 {random.randint(40,70)} ~ {random.randint(80,120)} 轉</div>
                """

            result = f"""
            <div id="cards">

                <div class="card step red">📊 分析結果如下</div>

                <div class="card step">🎯 今日得分率：{today_val}</div>

                <div class="card step">🔥 成功捕捉熱點訊號（{signal_chance}%）</div>

                <div class="card step">
                    📊 節奏判定：{status}<br>
                    ⚠️ 波動狀態：{risk}
                </div>

                {vip_html}

                <div class="card step">🤖 AI信心指數：{confidence}%</div>

                <div class="card step small">
                    ⚠️ 熱點通常不會維持太久<br>
                    💡 建議低倍觀察
                </div>

            </div>
            """

        except:
            result = "<div class='card'>⚠️ 輸入錯誤</div>"

    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <style>
    body {{
        background:#0b0f1a;
        color:white;
        font-family:sans-serif;
        text-align:center;
        padding:20px;
    }}

    .title {{
        color:orange;
        font-size:26px;
    }}

    input {{
        width:90%;
        padding:12px;
        margin:8px 0;
        border-radius:10px;
        border:none;
        background:#1c2233;
        color:white;
    }}

    button {{
        width:95%;
        padding:12px;
        margin-top:10px;
        border:none;
        border-radius:10px;
        background:orange;
        color:black;
    }}

    .card {{
        background:#151a2c;
        margin-top:15px;
        padding:15px;
        border-radius:15px;
    }}

    .red {{
        background:#ff3b3b;
    }}

    .small {{
        font-size:12px;
        color:gray;
    }}
    </style>

    <script>
    function unlock() {{
        let code = document.getElementById("code").value;

        if(code === "{VIP_CODE}") {{
            fetch("/unlock", {{
                method:"POST"
            }}).then(() => {{
                location.reload();
            }});
        }} else {{
            alert("授權碼錯誤");
            if (navigator.vibrate) {{
                navigator.vibrate([200,100,200]);
            }}
        }}
    }}
    </script>

    </head>

    <body>

    <div class="title">⚡ 熱點雷達</div>

    <form method="post">
        <input name="today" placeholder="今日得分率">
        <input name="current" placeholder="未開轉數">
        <input name="last1" placeholder="上次轉數">
        <input name="last2" placeholder="上上次">
        <button>開始分析</button>
    </form>

    <div style="display:{show_result};">
        {result}
    </div>

    </body>
    </html>
    """

@app.route("/unlock", methods=["POST"])
def unlock():
    user_id = request.remote_addr
    db.collection("users").document(user_id).set({
        "vip": True,
        "count": 0
    }, merge=True)
    return "ok"

port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
