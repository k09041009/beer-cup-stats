from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

# ==============================================================================
# 1. 擴充數據庫結構 (Data Schema) - 六大球隊、小字輩球員與即時賽況紀錄
# ==============================================================================
batters_db = [
    {
        "id": 1, "number": "1", "name": "王小明", "team": "台灣啤酒", 
        "position": "游擊手", "bat_pitch": "右投右打",
        "H": 14, "AB": 35, "BB": 6, "HBP": 1, "SAC": 2, "HR": 2, "RBI": 11,
        "last_games": [
            {"date": "6/01", "opp": "台北市大", "AB": 4, "H": 2, "HR": 0, "RBI": 1},
            {"date": "6/02", "opp": "台灣運彩", "AB": 3, "H": 1, "HR": 0, "RBI": 0},
            {"date": "6/03", "opp": "台南市", "AB": 4, "H": 3, "HR": 1, "RBI": 3},
            {"date": "5/28", "opp": "全越運動", "AB": 3, "H": 0, "HR": 0, "RBI": 0},
            {"date": "5/25", "opp": "桃園市", "AB": 4, "H": 1, "HR": 0, "RBI": 1}
        ]
    },
    {
        "id": 2, "number": "7", "name": "陳小同", "team": "台北市大", 
        "position": "中外野手", "bat_pitch": "右投左打",
        "H": 9, "AB": 27, "BB": 5, "HBP": 0, "SAC": 1, "HR": 1, "RBI": 7,
        "last_games": [
            {"date": "6/01", "opp": "台灣啤酒", "AB": 4, "H": 1, "HR": 0, "RBI": 0},
            {"date": "6/02", "opp": "台灣運彩", "AB": 4, "H": 2, "HR": 1, "RBI": 2},
            {"date": "6/03", "opp": "台南市", "AB": 3, "H": 0, "HR": 0, "RBI": 0},
            {"date": "5/28", "opp": "全越運動", "AB": 5, "H": 2, "HR": 0, "RBI": 1},
            {"date": "5/25", "opp": "桃園市", "AB": 3, "H": 1, "HR": 0, "RBI": 0}
        ]
    },
    {
        "id": 3, "number": "18", "name": "張小豪", "team": "台灣運彩", 
        "position": "指定打擊", "bat_pitch": "右投左打",
        "H": 16, "AB": 32, "BB": 4, "HBP": 2, "SAC": 0, "HR": 5, "RBI": 18,
        "last_games": [
            {"date": "6/01", "opp": "台灣啤酒", "AB": 4, "H": 3, "HR": 2, "RBI": 5},
            {"date": "6/02", "opp": "台北市大", "AB": 4, "H": 2, "HR": 0, "RBI": 1},
            {"date": "6/03", "opp": "台南市", "AB": 5, "H": 4, "HR": 1, "RBI": 3},
            {"date": "5/27", "opp": "全越運動", "AB": 3, "H": 1, "HR": 0, "RBI": 1},
            {"date": "5/24", "opp": "桃園市", "AB": 4, "H": 1, "HR": 0, "RBI": 0}
        ]
    },
    {
        "id": 4, "number": "31", "name": "林小華", "team": "台南市", 
        "position": "一壘手", "bat_pitch": "左投左打",
        "H": 8, "AB": 26, "BB": 3, "HBP": 1, "SAC": 1, "HR": 0, "RBI": 4,
        "last_games": [
            {"date": "6/01", "opp": "台灣啤酒", "AB": 3, "H": 1, "HR": 0, "RBI": 0},
            {"date": "6/02", "opp": "台北市大", "AB": 4, "H": 0, "HR": 0, "RBI": 0},
            {"date": "6/03", "opp": "台灣運彩", "AB": 3, "H": 2, "HR": 0, "RBI": 1},
            {"date": "5/27", "opp": "全越運動", "AB": 4, "H": 1, "HR": 0, "RBI": 0},
            {"date": "5/24", "opp": "桃園市", "AB": 3, "H": 1, "HR": 0, "RBI": 1}
        ]
    },
    {
        "id": 5, "number": "52", "name": "黃小鋒", "team": "全越運動", 
        "position": "左外野手", "bat_pitch": "右投右打",
        "H": 11, "AB": 30, "BB": 7, "HBP": 0, "SAC": 0, "HR": 3, "RBI": 12,
        "last_games": [
            {"date": "6/01", "opp": "台灣啤酒", "AB": 4, "H": 2, "HR": 1, "RBI": 2},
            {"date": "6/02", "opp": "台北市大", "AB": 4, "H": 1, "HR": 0, "RBI": 1},
            {"date": "6/03", "opp": "台灣運彩", "AB": 4, "H": 1, "HR": 1, "RBI": 2},
            {"date": "5/27", "opp": "台南市", "AB": 3, "H": 2, "HR": 0, "RBI": 3},
            {"date": "5/24", "opp": "桃園市", "AB": 4, "H": 0, "HR": 0, "RBI": 0}
        ]
    },
    {
        "id": 6, "number": "66", "name": "賴小宇", "team": "桃園市", 
        "position": "捕手", "bat_pitch": "右投右打",
        "H": 7, "AB": 24, "BB": 2, "HBP": 1, "SAC": 3, "HR": 0, "RBI": 3,
        "last_games": [
            {"date": "6/01", "opp": "台灣啤酒", "AB": 3, "H": 0, "HR": 0, "RBI": 0},
            {"date": "6/02", "opp": "台北市大", "AB": 3, "H": 1, "HR": 0, "RBI": 1},
            {"date": "6/03", "opp": "台灣運彩", "AB": 4, "H": 2, "HR": 0, "RBI": 0},
            {"date": "5/27", "opp": "台南市", "AB": 3, "H": 0, "HR": 0, "RBI": 0},
            {"date": "5/24", "opp": "全越運動", "AB": 3, "H": 1, "HR": 0, "RBI": 0}
        ]
    }
]

# 今日賽事基本資訊
today_match = {
    "team_A": "台灣啤酒",
    "team_B": "台北市大",
    "time": "18:30",
    "stadium": "天母棒球場",
    "weather": "晴朗 29°C"
}

# 原先的即時文字轉播紀錄 (Live Play-by-Play Logs)
live_logs = [
    {"time": "九局下", "event": "🎯 台灣啤酒 換代打！由【王小明】上場頂替。面對台北市大守護神，在兩好三壞滿球數下，鎖定一顆內角直球——轟！擊出右外野方向再見兩分全壘打！比賽結束！"},
    {"time": "八局上", "event": "🏃‍♂️ 台北市大 展開反攻！【陳小同】擊出中外野方向安打上壘，隨後靠著隊友犧牲觸擊推進至二壘。"},
    {"time": "六局下", "event": "🔥 台灣啤酒 攻勢再起！連續發動兩次盜壘成功，攻佔二三壘，現場氣氛沸騰！"},
    {"time": "四局下", "event": "💎 台灣啤酒 防守美技！游擊手展現流暢的接傳，精采抓到雙殺，化解失分危機。"},
    {"time": "一局上", "event": "⚾ 台啤盃 今日重頭戲正式開打！由台灣啤酒迎戰台北市大，首球投出，主審判定為好球！"}
]

# ==============================================================================
# 2. 運算層 (Core Logic)
# ==============================================================================
def process_data(search_query=None):
    processed = []
    for b in batters_db:
        pa = b["AB"] + b["BB"] + b["HBP"] + b["SAC"]
        avg = (b["H"] / b["AB"]) if b["AB"] > 0 else 0.0
        
        games = b["last_games"]
        g3_ab = sum(g["AB"] for g in games[:3])
        g3_h  = sum(g["H"] for g in games[:3])
        g3_avg = (g3_h / g3_ab) if g3_ab > 0 else 0.0
        
        g5_ab = sum(g["AB"] for g in games[:5])
        g5_h  = sum(g["H"] for g in games[:5])
        g5_avg = (g5_h / g5_ab) if g5_ab > 0 else 0.0
        
        search_target = f"{b['name']}{b['number']}{b['team']}".lower()
        if search_query and search_query.lower() not in search_target:
            continue
            
        p_dict = b.copy()
        p_dict.update({
            "pa": pa,
            "avg": f"{avg:.3f}".lstrip('0') if avg < 1.0 else f"{avg:.3f}",
            "g3_avg": f"{g3_avg:.3f}".lstrip('0') if g3_avg < 1.0 else f"{g3_avg:.3f}",
            "g5_avg": f"{g5_avg:.3f}".lstrip('0') if g5_avg < 1.0 else f"{g5_avg:.3f}",
            "avg_raw": avg, "g3_raw": g3_avg, "g5_raw": g5_avg
        })
        processed.append(p_dict)
    return processed

# ==============================================================================
# 3. 展示層 (HTML 介面 - 全面台啤盃冠名化)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>台啤盃 - 轉播即時文字導播數據系統</title>
    <style>
        body { font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 0; background-color: #f0f2f5; color: #333; }
        .header { background: linear-gradient(135deg, #0d5c3a, #11422c); color: white; padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .nav-tabs { display: flex; justify-content: center; background: #fff; border-bottom: 2px solid #0d5c3a; margin-bottom: 20px; }
        .tab { padding: 15px 30px; cursor: pointer; font-weight: bold; color: #555; text-decoration: none; border-bottom: 3px solid transparent; }
        .tab:hover, .tab.active { color: #0d5c3a; border-bottom: 3px solid #0d5c3a; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .card { background: white; border-radius: 10px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 25px; }
        .search-box { width: 100%; max-width: 500px; padding: 12px; font-size: 16px; border: 2px solid #ddd; border-radius: 6px; margin-bottom: 20px; box-sizing: border-box; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: center; border-bottom: 1px solid #eee; }
        th { background-color: #0d5c3a; color: white; }
        .badge { background: #e2f0d9; color: #0d5c3a; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 13px; }
        .rank-number { font-size: 18px; font-weight: bold; color: #ff9800; }
        .flex-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .btn { padding: 5px 10px; background: #0d5c3a; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; font-size: 12px; }
        
        /* 即時文字轉播專用樣式 */
        .log-container { max-height: 300px; overflow-y: auto; background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 8px; font-family: 'Consolas', monospace, 'Microsoft JhengHei'; }
        .log-item { margin-bottom: 12px; line-height: 1.6; border-bottom: 1px solid #2d2d2d; padding-bottom: 8px; }
        .log-time { color: #4fc1ff; font-weight: bold; margin-right: 10px; }
    </style>
</head>
<body>

    <div class="header">
        <h1>🏆 台啤盃全國棒球菁英賽 - 轉播即時數據系統 🏆</h1>
        <p>六大勁旅戰力整合面板（台灣啤酒、台北市大、台灣運彩、台南市、全越運動、桃園市）</p>
    </div>

    <div class="nav-tabs">
        <a href="/" class="tab {% if active_tab=='home' %}active{% endif %}">🏏 球員名冊與搜尋</a>
        <a href="/leaderboard" class="tab {% if active_tab=='leader' %}active{% endif %}">🏆 台啤盃數據榜</a>
        <a href="/match" class="tab {% if active_tab=='match' %}active{% endif %}">📺 今日賽事與即時紀錄</a>
    </div>

    <div class="container">
        
        {% if active_tab == 'home' %}
        <!-- 新增：首頁頂部置頂最新即時賽況 -->
        <div class="card" style="border-left: 6px solid #dc3545;">
            <h3 style="color: #dc3545; margin-top: 0;">⚡ 台啤盃戰況最前線（最新賽事紀錄）</h3>
            <div class="log-container" style="max-height: 100px;">
                <div class="log-item" style="border: none; margin: 0; padding: 0;">
                    <span class="log-time">{{ logs[0].time }}</span> {{ logs[0].event }}
                </div>
            </div>
        </div>

        <div class="card">
            <h2>🔍 台啤盃球員快速搜尋</h2>
            <form method="GET" action="/">
                <input type="text" name="q" class="search-box" placeholder="搜尋球員(如:王小明)、背號(#1)、或球隊..." value="{{ query }}">
                <button type="submit" class="btn" style="padding: 12px 20px; font-size: 16px; margin-left: 10px;">搜尋</button>
                {% if query %}<a href="/" style="margin-left:10px; color:#999;">清除搜尋</a>{% endif %}
            </form>

            <table>
                <thead>
                    <tr>
                        <th>背號</th>
                        <th>球員基本履歷</th>
                        <th>所屬球隊</th>
                        <th>投打習慣</th>
                        <th>賽季數據 (AVG / HR / RBI)</th>
                        <th>近期近況打擊率 (近3場 / 近5場)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in players %}
                    <tr>
                        <td style="font-size: 20px; font-weight: bold; color: #666;">#{{ p.number }}</td>
                        <td style="text-align: left;">
                            <strong style="font-size: 18px;">{{ p.name }}</strong> <span class="badge">{{ p.position }}</span>
                        </td>
                        <td><strong>{{ p.team }}</strong></td>
                        <td><small style="color:#777;">{{ p.bat_pitch }}</small></td>
                        <td>
                            <strong style="color:#0d5c3a;">{{ p.avg }}</strong> / {{ p.HR }}支 / {{ p.RBI }}分
                        </td>
                        <td>
                            <span style="color: #2196F3;">近3場: <strong>{{ p.g3_avg }}</strong></span><br>
                            <span style="color: #673AB7;">近5場: <strong>{{ p.g5_avg }}</strong></span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        {% if active_tab == 'leader' %}
        <h2>🏆 台啤盃個人數據領先榜 (打擊三冠王)</h2>
        <div class="flex-grid">
            <div class="card">
                <h3>🟢 打擊率排行榜 (AVG)</h3>
                <table>
                    {% for p in ranks.avg %}
                    <tr>
                        <td class="rank-number">{{ loop.index }}</td>
                        <td><strong>{{ p.name }}</strong> ({{ p.team }})</td>
                        <td style="font-weight: bold; color:#0d5c3a;">{{ p.avg }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            <div class="card">
                <h3>🔴 全壘打排行榜 (HR)</h3>
                <table>
                    {% for p in ranks.hr %}
                    <tr>
                        <td class="rank-number">{{ loop.index }}</td>
                        <td><strong>{{ p.name }}</strong> ({{ p.team }})</td>
                        <td style="font-weight: bold; color:#dc3545;">{{ p.HR }} 支</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            <div class="card">
                <h3>🔵 打點排行榜 (RBI)</h3>
                <table>
                    {% for p in ranks.rbi %}
                    <tr>
                        <td class="rank-number">{{ loop.index }}</td>
                        <td><strong>{{ p.name }}</strong> ({{ p.team }})</td>
                        <td style="font-weight: bold; color:#007bff;">{{ p.RBI }} 分</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
        {% endif %}

        {% if active_tab == 'match' %}
        <div class="card" style="background: linear-gradient(to right, #ffffff, #edf7ee); border-left: 6px solid #0d5c3a;">
            <h2>📺 台啤盃今日賽事轉播面板</h2>
            <p style="font-size: 18px;">🏟️ <strong>今日戰場：</strong> {{ match_info.stadium }} | 🕒 預計開打：{{ match_info.time }} | ☀️ 氣象狀況：{{ match_info.weather }}</p>
            <div style="display: flex; justify-content: space-around; align-items: center; margin-top: 30px;">
                <div style="text-align: center;">
                    <h3 style="font-size: 28px; color: #0d5c3a; margin:0;">{{ match_info.team_A }}</h3>
                    <p style="color:#666;">(主場一壘側)</p>
                </div>
                <div style="font-size: 24px; font-weight: bold; color: #999;">VS</div>
                <div style="text-align: center;">
                    <h3 style="font-size: 28px; color: #cc7a00; margin:0;">{{ match_info.team_B }}</h3>
                    <p style="color:#666;">(客場三壘側)</p>
                </div>
            </div>
        </div>

        <!-- 核心功能重現：原先的文字即時紀錄區塊 -->
        <div class="card">
            <h3>⏱️ 台啤盃即時文字轉播紀錄流 (Play-by-Play)</h3>
            <div class="log-container">
                {% for log in logs %}
                <div class="log-item">
                    <span class="log-time">[{{ log.time }}]</span>
                    <span>{{ log.event }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="card">
            <h3>🔥 兩隊焦點球員近況變化（主播播報素材）</h3>
            <table>
                <thead>
                    <tr>
                        <th>所屬球隊</th>
                        <th>背號</th>
                        <th>球員姓名</th>
                        <th>守備位置</th>
                        <th>賽季打擊率</th>
                        <th>近 3 場打擊率</th>
                        <th>播報指引趨勢</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in players %}
                    {% if p.team == match_info.team_A or p.team == match_info.team_B %}
                    <tr>
                        <td><strong>{{ p.team }}</strong></td>
                        <td>#{{ p.number }}</td>
                        <td><strong>{{ p.name }}</strong></td>
                        <td><span class="badge">{{ p.position }}</span></td>
                        <td style="font-weight: bold;">{{ p.avg }}</td>
                        <td style="color: #2196F3; font-weight: bold;">{{ p.g3_avg }}</td>
                        <td>
                            {% if p.g3_raw > p.avg_raw %}
                            <span style="color: #ff9800; font-weight: bold;">📈 近期打擊手感火燙</span>
                            {% else %}
                            <span style="color: #9e9e9e;">📊 穩定發揮持平中</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

    </div>

</body>
</html>
"""

# ==============================================================================
# 4. 路由與網頁控制層 (Controller)
# ==============================================================================
@app.route('/')
def home():
    query = request.args.get('q', '')
    players = process_data(search_query=query)
    return render_template_string(HTML_TEMPLATE, active_tab='home', players=players, query=query, logs=live_logs)

@app.route('/leaderboard')
def leaderboard():
    players = process_data()
    ranks = {
        "avg": sorted(players, key=lambda x: x["avg_raw"], reverse=True),
        "hr": sorted(players, key=lambda x: x["HR"], reverse=True),
        "rbi": sorted(players, key=lambda x: x["RBI"], reverse=True)
    }
    return render_template_string(HTML_TEMPLATE, active_tab='leader', ranks=ranks)

@app.route('/match')
def match():
    players = process_data()
    return render_template_string(HTML_TEMPLATE, active_tab='match', players=players, match_info=today_match, logs=live_logs)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)