from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import os

app = Flask(__name__)

# ==============================================================================
# 1. 聯賽動態資料庫 (初始範本)
# ==============================================================================
TEAMS = ["台灣啤酒", "台北市大", "台灣運彩", "台南市", "全越運動", "桃園市"]

ALL_PLAYERS = [
    {"id": 1, "number": "1", "name": "王小明", "team": "台灣啤酒", "position": "游擊手", "type": "batter"},
    {"id": 2, "number": "7", "name": "陳小同", "team": "台北市大", "position": "中外野手", "type": "batter"},
    {"id": 7, "number": "17", "name": "林投手", "team": "台灣啤酒", "position": "投手", "type": "pitcher"},
    {"id": 8, "number": "99", "name": "黃終結", "team": "台北市大", "position": "投手", "type": "pitcher"}
]

CUMULATIVE_BASE_BATTERS = {
    1: {"H": 12, "AB": 30, "BB": 5, "HBP": 1, "SAC": 2},
    2: {"H": 8, "AB": 25, "BB": 3, "HBP": 0, "SAC": 1}
}
CUMULATIVE_BASE_PITCHERS = {
    7: {"IP_outs": 36, "balls_total": 195, "strikes": 130, "ER": 6, "K": 18},
    8: {"IP_outs": 6, "balls_total": 30, "strikes": 21, "ER": 1, "K": 3}
}

matches_db = [
    {
        "id": 1,
        "team_A": "台灣啤酒",
        "team_B": "台北市大",
        "date": "2026-06-04",
        "time": "18:30",
        "stadium": "天母棒球場",
        "status": "進行中",
        "batters": {
            1: {"H": 2, "AB": 3, "BB": 1, "HBP": 0, "SAC": 0},
            2: {"H": 1, "AB": 2, "BB": 1, "HBP": 0, "SAC": 0}
        },
        "pitchers": {
            7: {"IP_outs": 9, "balls_total": 45, "strikes": 30, "ER": 1, "K": 4},
            8: {"IP_outs": 3, "balls_total": 15, "strikes": 11, "ER": 0, "K": 2}
        }
    }
]

# ==============================================================================
# 2. 核心運算邏輯
# ==============================================================================
def get_cumulative_stats():
    batters = {p["id"]: {**CUMULATIVE_BASE_BATTERS.get(p["id"], {"H":0,"AB":0,"BB":0,"HBP":0,"SAC":0})} for p in ALL_PLAYERS if p["type"] == "batter"}
    pitchers = {p["id"]: {**CUMULATIVE_BASE_PITCHERS.get(p["id"], {"IP_outs":0,"balls_total":0,"strikes":0,"ER":0,"K":0})} for p in ALL_PLAYERS if p["type"] == "pitcher"}
    
    for m in matches_db:
        for p_id, stats in m["batters"].items():
            if p_id in batters:
                for k in stats: batters[p_id][k] = batters[p_id].get(k, 0) + stats.get(k, 0)
        for p_id, stats in m["pitchers"].items():
            if p_id in pitchers:
                for k in stats: pitchers[p_id][k] = pitchers[p_id].get(k, 0) + stats.get(k, 0)
                
    processed_batters = []
    for p in ALL_PLAYERS:
        if p["type"] == "batter":
            b_stat = batters.get(p["id"], {"H":0,"AB":0,"BB":0,"HBP":0,"SAC":0})
            pa = b_stat["AB"] + b_stat["BB"] + b_stat["HBP"] + b_stat["SAC"]
            avg = b_stat["H"] / b_stat["AB"] if b_stat["AB"] > 0 else 0.0
            obp = (b_stat["H"] + b_stat["BB"] + b_stat["HBP"]) / pa if pa > 0 else 0.0
            processed_batters.append({
                **p, **b_stat, "PA": pa,
                "AVG": f"{avg:.3f}".lstrip('0') if avg < 1.0 else f"{avg:.3f}",
                "OBP": f"{obp:.3f}".lstrip('0') if obp < 1.0 else f"{obp:.3f}"
            })
            
    processed_pitchers = []
    for p in ALL_PLAYERS:
        if p["type"] == "pitcher":
            p_stat = pitchers.get(p["id"], {"IP_outs":0,"balls_total":0,"strikes":0,"ER":0,"K":0})
            outs = p_stat["IP_outs"]
            era = (p_stat["ER"] * 9) / (outs / 3) if outs > 0 else 0.0
            strike_rate = (p_stat["strikes"] / p_stat["balls_total"] * 100) if p_stat["balls_total"] > 0 else 0.0
            k9 = (p_stat["K"] * 9) / (outs / 3) if outs > 0 else 0.0
            processed_pitchers.append({
                **p, **p_stat, "IP": f"{outs // 3}.{outs % 3}", "ERA": f"{era:.2f}",
                "STRIKE_RATE": f"{strike_rate:.1f}%", "K9": f"{k9:.2f}"
            })
            
    return processed_batters, processed_pitchers

# ==============================================================================
# 3. HTML 範本區塊
# ==============================================================================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>台啤盃 - 賽程數據整合系統</title>
    <link href="https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.css" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@5.11.3/main.min.js"></script>
    <style>
        body { font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 0; background-color: #121212; color: #e0e0e0; }
        .header { background: linear-gradient(135deg, #0d5c3a, #164e33); color: white; padding: 20px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        .nav-tabs { display: flex; justify-content: center; background: #1e1e1e; border-bottom: 3px solid #1b7339; }
        .tab { padding: 15px 35px; cursor: pointer; font-weight: bold; color: #bbb; text-decoration: none; border-bottom: 4px solid transparent; transition: 0.2s; }
        .tab:hover, .tab.active { color: #2ecc71; border-bottom: 4px solid #2ecc71; background: #252525; }
        .container { max-width: 1300px; margin: 0 auto; padding: 25px; }
        .card { background: #1e1e1e; border-radius: 12px; padding: 25px; box-shadow: 0 6px 16px rgba(0,0,0,0.4); margin-bottom: 30px; border: 1px solid #2d2d2d; }
        
        .module-title { font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 15px; color: #fff; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; background-color: #151515; }
        th { background-color: #1b7339; color: white; padding: 12px; font-size: 14px; font-weight: bold; text-align: center; }
        td { padding: 14px; text-align: center; border-bottom: 1px solid #2a2a2a; font-size: 15px; color: #fff; }
        tr:hover { background-color: #222; }
        
        .flex-grid { display: flex; gap: 20px; margin-bottom: 25px; flex-wrap: wrap; }
        .flex-child { flex: 1; min-width: 300px; }
        
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 12px; }
        .form-control { width: 100%; padding: 10px; background: #2a2a2a; border: 1px solid #444; color: white; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .btn { padding: 11px 20px; background: #1b7339; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #228b4c; }
        
        .btn-group { display: flex; gap: 6px; justify-content: center; }
        .btn-input { padding: 6px 12px; font-size: 12px; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; color: white; }
        .b-h { background-color: #1b7339; } .b-out { background-color: #d93025; } .b-bb { background-color: #1a73e8; } .b-hbp { background-color: #00bcd4; } .b-sac { background-color: #f1a80a; }
        
        #calendar { background: #1a1a1a; padding: 20px; border-radius: 8px; color: #fff; border: 1px solid #333; }
        .fc-theme-standard td, .fc-theme-standard th { border: 1px solid #333 !important; }
        .fc-daygrid-day:hover { background-color: #252525; cursor: pointer; }
        .fc-event { background-color: #1b7339 !important; border: 1px solid #2ecc71 !important; color: white !important; padding: 3px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏆 台啤盃棒球聯賽 - 賽程數據整合系統 🏆</h1>
    </div>
    <div class="nav-tabs">
        <a href="/" class="tab {% if active_tab=='calendar' %}active{% endif %}">🗓️ 台啤盃賽程與球隊管理</a>
        <a href="/cumulative" class="tab {% if active_tab=='cumulative' %}active{% endif %}">🏆 盃賽累積數據榜</a>
    </div>
    <div class="container">
        [[INJECT_CONTENT_HERE]]
    </div>
</body>
</html>
"""

# ==============================================================================
# 4. 路由設定
# ==============================================================================
@app.route('/')
def index():
    calendar_content = """
    <div class="flex-grid">
        <div class="card flex-child">
            <h3 style="margin-top:0; color:#2ecc71;">🛡️ 新增參賽球隊</h3>
            <form method="POST" action="/add-team">
                <div style="display:flex; gap:10px;">
                    <input type="text" name="team_name" class="form-control" placeholder="輸入新球隊名稱" required>
                    <button type="submit" class="btn">新增球隊</button>
                </div>
            </form>
            <div style="margin-top:15px;">
                <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:5px;">
                    {% for team in teams %}
                    <span style="background:#2d2d2d; padding:4px 10px; border-radius:15px; font-size:13px; border:1px solid #444;">{{ team }}</span>
                    {% endfor %}
                </div>
            </div>
        </div>
        <div class="card flex-child" style="flex: 1.5;">
            <h3 style="margin-top:0; color:#3498db;">👤 註冊全新球員</h3>
            <form method="POST" action="/add-player">
                <div class="form-grid">
                    <input type="text" name="name" class="form-control" placeholder="球員姓名" required>
                    <input type="text" name="number" class="form-control" placeholder="背號" required>
                    <select name="team" class="form-control" required>
                        <option value="" disabled selected>選擇所屬球隊</option>
                        {% for team in teams %} <option value="{{ team }}">{{ team }}</option> {% endfor %}
                    </select>
                    <select name="position" class="form-control" required>
                        <option value="投手">投手</option>
                        <option value="捕手">捕手</option>
                        <option value="一壘手">一壘手</option>
                        <option value="游擊手">游擊手</option>
                        <option value="中外野手">中外野手</option>
                        <option value="指定打擊">指定打擊</option>
                    </select>
                    <select name="type" class="form-control" required>
                        <option value="batter">打者身分</option>
                        <option value="pitcher">投手身分</option>
                    </select>
                </div>
                <button type="submit" class="btn" style="background:#3498db;">登錄選手</button>
            </form>
        </div>
    </div>
    <div class="card">
        <h3 style="margin-top:0;">➕ 排定常規賽程</h3>
        <form method="POST" action="/add-match">
            <div class="form-grid">
                <div><select name="team_A" class="form-control" required>{% for team in teams %}<option value="{{ team }}">{{ team }}</option>{% endfor %}</select></div>
                <div><select name="team_B" class="form-control" required>{% for team in teams %}<option value="{{ team }}">{{ team }}</option>{% endfor %}</select></div>
                <div><input type="date" name="date" class="form-control" required></div>
                <div><input type="time" name="time" class="form-control" required></div>
                <div><input type="text" name="stadium" class="form-control" placeholder="比賽球場" required></div>
            </div>
            <button type="submit" class="btn">排定對戰</button>
        </form>
    </div>
    <div class="card">
        <h3 style="margin-top:0; color:#2ecc71;">🗓️ 大會官方時程行事曆</h3>
        <div id="calendar"></div>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
                initialView: 'dayGridMonth', locale: 'zh-tw', editable: false,
                events: [
                    {% for m in matches %} { id: '{{ m.id }}', title: '{{ m.team_A }} VS {{ m.team_B }}', start: '{{ m.date }}T{{ m.time }}', url: '/match/{{ m.id }}' }, {% endfor %}
                ]
            });
            calendar.render();
        });
    </script>
    """
    return render_template_string(BASE_TEMPLATE.replace('[[INJECT_CONTENT_HERE]]', calendar_content), active_tab='calendar', teams=TEAMS, matches=matches_db)

@app.route('/add-team', methods=['POST'])
def add_team():
    team_name = request.form.get('team_name').strip()
    if team_name and team_name not in TEAMS: TEAMS.append(team_name)
    return redirect(url_for('index'))

@app.route('/add-player', methods=['POST'])
def add_player():
    ALL_PLAYERS.append({
        "id": len(ALL_PLAYERS) + 1, "name": request.form.get('name'), "number": request.form.get('number'),
        "team": request.form.get('team'), "position": request.form.get('position'), "type": request.form.get('type')
    })
    return redirect(url_for('index'))

@app.route('/add-match', methods=['POST'])
def add_match():
    team_a, team_b = request.form.get('team_A'), request.form.get('team_B')
    match_batters, match_pitchers = {}, {}
    for p in ALL_PLAYERS:
        if p["team"] in [team_a, team_b]:
            if p["type"] == "batter": match_batters[p["id"]] = {"H":0,"AB":0,"BB":0,"HBP":0,"SAC":0}
            elif p["type"] == "pitcher": match_pitchers[p["id"]] = {"IP_outs":0,"balls_total":0,"strikes":0,"ER":0,"K":0}
    matches_db.append({
        "id": len(matches_db) + 1, "team_A": team_a, "team_B": team_b, "date": request.form.get('date'),
        "time": request.form.get('time'), "stadium": request.form.get('stadium'),
        "batters": match_batters, "pitchers": match_pitchers
    })
    return redirect(url_for('index'))

@app.route('/cumulative')
def cumulative():
    c_batters, c_pitchers = get_cumulative_stats()
    content = """
    <div class="card"><div class="module-title">🏏 打者累積數據</div>
        <table>
            <tr><th>球員</th><th>球隊</th><th>PA</th><th>AB</th><th>H</th><th>BB</th><th>HBP</th><th>SAC</th><th>AVG</th><th>OBP</th></tr>
            {% for p in batters %}<tr><td>{{ p.name }}</td><td>{{ p.team }}</td><td>{{ p.PA }}</td><td>{{ p.AB }}</td><td>{{ p.H }}</td><td>{{ p.BB }}</td><td>{{ p.HBP }}</td><td>{{ p.SAC }}</td><td style="color:#2ecc71;">{{ p.AVG }}</td><td>{{ p.OBP }}</td></tr>{% endfor %}
        </table>
    </div>
    <div class="card"><div class="module-title">⚾ 投手累積數據</div>
        <table>
            <tr><th>球員</th><th>球隊</th><th>IP</th><th>總球數</th><th>好球</th><th>ER</th><th>K</th><th>ERA</th><th>好球率</th></tr>
            {% for p in pitchers %}<tr><td>{{ p.name }}</td><td>{{ p.team }}</td><td>{{ p.IP }}</td><td>{{ p.balls_total }}</td><td>{{ p.strikes }}</td><td>{{ p.ER }}</td><td>{{ p.K }}</td><td style="color:#2ecc71;">{{ p.ERA }}</td><td>{{ p.STRIKE_RATE }}</td></tr>{% endfor %}
        </table>
    </div>
    """
    return render_template_string(BASE_TEMPLATE.replace('[[INJECT_CONTENT_HERE]]', content), active_tab='cumulative', batters=c_batters, pitchers=c_pitchers)

@app.route('/match/<int:match_id>')
def match_room(match_id):
    match = next((m for m in matches_db if m["id"] == match_id), None)
    if not match: return "賽事不存在", 404
        
    m_batters, m_pitchers = [], []
    for p in ALL_PLAYERS:
        if p["team"] in [match["team_A"], match["team_B"]]:
            if p["type"] == "batter":
                stat = match["batters"].get(p["id"], {"H":0,"AB":0,"BB":0,"HBP":0,"SAC":0})
                m_batters.append({**p, **stat})
            elif p["type"] == "pitcher":
                stat = match["pitchers"].get(p["id"], {"IP_outs":0,"balls_total":0,"strikes":0,"ER":0,"K":0})
                m_pitchers.append({**p, **stat})

    match_template = """
    <div class="card" style="border-left: 6px solid #2ecc71;">
        <h2>🏟️ {{ match.stadium }} | {{ match.team_A }} VS {{ match.team_B }}</h2>
        <a href="/" style="color:#aaa;">⬅️ 回到行事曆</a>
    </div>

    <div class="card">
        <div class="module-title">🏏 打者單場 LIVE (Batting)</div>
        <table>
            <tr><th>球員</th><th>球隊</th><th>PA</th><th>AB</th><th>H</th><th>BB</th><th>HBP</th><th>SAC</th><th>單場AVG</th><th>動作紀錄</th></tr>
            {% for p in batters %}
            <tr>
                <td>{{ p.name }}</td><td>{{ p.team }}</td>
                <td id="b-pa-{{ p.id }}">0</td><td id="b-ab-{{ p.id }}">{{ p.AB }}</td><td id="b-h-{{ p.id }}">{{ p.H }}</td><td id="b-bb-{{ p.id }}">{{ p.BB }}</td><td id="b-hbp-{{ p.id }}">{{ p.HBP }}</td><td id="b-sac-{{ p.id }}">{{ p.SAC }}</td>
                <td id="b-avg-{{ p.id }}" style="color:#2ecc71; font-weight:bold;">.000</td>
                <td>
                    <div class="btn-group">
                        <button class="btn-input b-h" onclick="sendAction({{ match.id }}, 'batter', {{ p.id }}, 'H')">H</button>
                        <button class="btn-input b-out" onclick="sendAction({{ match.id }}, 'batter', {{ p.id }}, 'OUT')">OUT</button>
                        <button class="btn-input b-bb" onclick="sendAction({{ match.id }}, 'batter', {{ p.id }}, 'BB')">BB</button>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <div class="card">
        <div class="module-title">⚾ 投手單場 LIVE (Pitching)</div>
        <table>
            <tr><th>球員</th><th>球隊</th><th>IP</th><th>總球數</th><th>好球</th><th>ER</th><th>K</th><th>單場ERA</th><th>動作紀錄</th></tr>
            {% for p in pitchers %}
            <tr>
                <td>{{ p.name }}</td><td>{{ p.team }}</td>
                <td id="p-ip-{{ p.id }}">0.0</td><td id="p-total-{{ p.id }}">{{ p.balls_total }}</td><td id="p-strikes-{{ p.id }}">{{ p.strikes }}</td><td id="p-er-{{ p.id }}">{{ p.ER }}</td><td id="p-k-{{ p.id }}">{{ p.K }}</td>
                <td id="p-era-{{ p.id }}" style="color:#2ecc71;">0.00</td>
                <td>
                    <div class="btn-group">
                        <button class="btn-input b-h" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'STRIKE')">好球</button>
                        <button class="btn-input b-bb" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'BALL')">壞球</button>
                        <button class="btn-input b-out" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'OUT')">出局</button>
                        <button class="btn-input b-sac" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'ER')">失分</button>
                        <button class="btn-input b-hbp" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'K')">三振</button>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>

    <script>
        // 【強化防護網】使用預設值 0 確保不會出現 undefined
        const batters = { {% for p in batters %} "{{ p.id }}": { h: {{ p.H|default(0) }}, ab: {{ p.AB|default(0) }}, bb: {{ p.BB|default(0) }}, hbp: {{ p.HBP|default(0) }}, sac: {{ p.SAC|default(0) }} }, {% endfor %} };
        const pitchers = { {% for p in pitchers %} "{{ p.id }}": { outs: {{ p.IP_outs|default(0) }}, total: {{ p.balls_total|default(0) }}, strikes: {{ p.strikes|default(0) }}, er: {{ p.ER|default(0) }}, k: {{ p.K|default(0) }} }, {% endfor %} };

        function runCalcBatter(id) {
            let b = batters[id];
            let pa = (b.ab||0) + (b.bb||0) + (b.hbp||0) + (b.sac||0);
            let avg = b.ab > 0 ? (b.h / b.ab) : 0;
            document.getElementById(`b-pa-${id}`).innerText = pa;
            document.getElementById(`b-ab-${id}`).innerText = b.ab||0;
            document.getElementById(`b-h-${id}`).innerText = b.h||0;
            document.getElementById(`b-bb-${id}`).innerText = b.bb||0;
            document.getElementById(`b-hbp-${id}`).innerText = b.hbp||0;
            document.getElementById(`b-sac-${id}`).innerText = b.sac||0;
            document.getElementById(`b-avg-${id}`).innerText = avg === 1 ? "1.000" : avg.toFixed(3).substring(1);
        }

        function runCalcPitcher(id) {
            let p = pitchers[id];
            document.getElementById(`p-ip-${id}`).innerText = `${Math.floor((p.outs||0)/3)}.${(p.outs||0)%3}`;
            document.getElementById(`p-total-${id}`).innerText = p.total||0;
            document.getElementById(`p-strikes-${id}`).innerText = p.strikes||0;
            document.getElementById(`p-er-${id}`).innerText = p.er||0;
            document.getElementById(`p-k-${id}`).innerText = p.k||0;
            document.getElementById(`p-era-${id}`).innerText = p.outs > 0 ? (((p.er||0) * 9) / (p.outs / 3)).toFixed(2) : "0.00";
        }

        function sendAction(matchId, pType, pId, action) {
            fetch(`/api/update-record`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ match_id: matchId, player_type: pType, player_id: pId, action_type: action })
            })
            .then(res => res.json())
            .then(data => {
                if(data.success) {
                    if (pType === 'batter') {
                        // 【強化防護網】確保 API 回傳大寫鍵值，如果缺漏自動補 0
                        batters[pId] = { h: data.new_data.H || 0, ab: data.new_data.AB || 0, bb: data.new_data.BB || 0, hbp: data.new_data.HBP || 0, sac: data.new_data.SAC || 0 };
                        runCalcBatter(pId);
                    } else {
                        pitchers[pId] = { outs: data.new_data.IP_outs || 0, total: data.new_data.balls_total || 0, strikes: data.new_data.strikes || 0, er: data.new_data.ER || 0, k: data.new_data.K || 0 };
                        runCalcPitcher(pId);
                    }
                }
            });
        }

        window.onload = function() {
            Object.keys(batters).forEach(id => runCalcBatter(id));
            Object.keys(pitchers).forEach(id => runCalcPitcher(id));
        };
    </script>
    """
    return render_template_string(BASE_TEMPLATE.replace('[[INJECT_CONTENT_HERE]]', match_template), active_tab='calendar', match=match, batters=m_batters, pitchers=m_pitchers)

@app.route('/api/update-record', methods=['POST'])
def api_update_record():
    data = request.json
    match = next((m for m in matches_db if m["id"] == data.get("match_id")), None)
    if not match: return jsonify({"success": False})
        
    p_id, action = int(data.get("player_id")), data.get("action_type")
    if data.get("player_type") == "batter":
        stat = match["batters"].setdefault(p_id, {"H": 0, "AB": 0, "BB": 0, "HBP": 0, "SAC": 0})
        if action == "H": stat["H"] += 1; stat["AB"] += 1
        elif action == "OUT": stat["AB"] += 1
        elif action == "BB": stat["BB"] += 1
        elif action == "HBP": stat["HBP"] += 1
        elif action == "SAC": stat["SAC"] += 1
        return jsonify({"success": True, "new_data": stat})
        
    elif data.get("player_type") == "pitcher":
        stat = match["pitchers"].setdefault(p_id, {"IP_outs": 0, "balls_total": 0, "strikes": 0, "ER": 0, "K": 0})
        if action == "STRIKE": stat["strikes"] += 1; stat["balls_total"] += 1
        elif action == "BALL": stat["balls_total"] += 1
        elif action == "OUT": stat["IP_outs"] += 1; stat["strikes"] += 1; stat["balls_total"] += 1
        elif action == "ER": stat["ER"] += 1
        elif action == "K": stat["K"] += 1; stat["IP_outs"] += 1; stat["strikes"] += 1; stat["balls_total"] += 1
        return jsonify({"success": True, "new_data": stat})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)