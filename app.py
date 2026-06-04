from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import os

app = Flask(__name__)

# ==============================================================================
# 1. 聯賽基礎靜態資料 (台啤盃六大勁旅 & 選手名冊範本)
# ==============================================================================
TEAMS = ["台灣啤酒", "台北市大", "台灣運彩", "台南市", "全越運動", "桃園市"]

ALL_PLAYERS = [
    {"id": 1, "number": "1", "name": "王小明", "team": "台灣啤酒", "position": "游擊手", "type": "batter"},
    {"id": 2, "number": "7", "name": "陳小同", "team": "台北市大", "position": "中外野手", "type": "batter"},
    {"id": 3, "number": "18", "name": "張小豪", "team": "台灣運彩", "position": "指定打擊", "type": "batter"},
    {"id": 4, "number": "31", "name": "林小華", "team": "台南市", "position": "一壘手", "type": "batter"},
    {"id": 5, "number": "52", "name": "黃小鋒", "team": "全越運動", "position": "左外野手", "type": "batter"},
    {"id": 6, "number": "66", "name": "賴小宇", "team": "桃園市", "position": "捕手", "type": "batter"},
    {"id": 7, "number": "17", "name": "林投手", "team": "台灣啤酒", "position": "投手", "type": "pitcher"},
    {"id": 8, "number": "99", "name": "黃終結", "team": "台北市大", "position": "投手", "type": "pitcher"},
    {"id": 9, "number": "58", "name": "張小投", "team": "台灣運彩", "position": "投手", "type": "pitcher"},
    {"id": 10, "number": "46", "name": "陳小投", "team": "台南市", "position": "投手", "type": "pitcher"}
]

# 歷史盃賽累積基礎數據 (在沒有打任何單場新賽事前的累積底線)
CUMULATIVE_BASE_BATTERS = {
    1: {"H": 12, "AB": 30, "BB": 5, "HBP": 1, "SAC": 2},
    2: {"H": 8, "AB": 25, "BB": 3, "HBP": 0, "SAC": 1},
    3: {"H": 15, "AB": 30, "BB": 3, "HBP": 2, "SAC": 0},
    4: {"H": 7, "AB": 24, "BB": 2, "HBP": 1, "SAC": 1},
    5: {"H": 10, "AB": 28, "BB": 6, "HBP": 0, "SAC": 0},
    6: {"H": 6, "AB": 22, "BB": 2, "HBP": 1, "SAC": 2}
}

CUMULATIVE_BASE_PITCHERS = {
    7: {"IP_outs": 36, "balls_total": 195, "strikes": 130, "ER": 6, "K": 18}, # 12.0局
    8: {"IP_outs": 6, "balls_total": 30, "strikes": 21, "ER": 1, "K": 3},      # 2.0局
    9: {"IP_outs": 30, "balls_total": 150, "strikes": 98, "ER": 5, "K": 11},   # 10.0局
    10: {"IP_outs": 24, "balls_total": 135, "strikes": 82, "ER": 9, "K": 8}    # 8.0局
}

# ==============================================================================
# 2. 記憶體賽程與單場數據庫 (動態新增與操作區)
# ==============================================================================
matches_db = [
    {
        "id": 1,
        "team_A": "台灣啤酒",
        "team_B": "台北市大",
        "date": "2026-06-04",
        "time": "18:30",
        "stadium": "天母棒球場",
        "status": "進行中",
        # 單場獨立數據紀錄
        "batters": {
            1: {"H": 2, "AB": 3, "BB": 1, "HBP": 0, "SAC": 0},
            2: {"H": 1, "AB": 2, "BB": 1, "HBP": 0, "SAC": 0}
        },
        "pitchers": {
            7: {"IP_outs": 9, "balls_total": 45, "strikes": 30, "ER": 1, "K": 4}, # 3.0局
            8: {"IP_outs": 3, "balls_total": 15, "strikes": 11, "ER": 0, "K": 2}  # 1.0局
        }
    },
    {
        "id": 2,
        "team_A": "台灣運彩",
        "team_B": "台南市",
        "date": "2026-06-12",
        "time": "14:00",
        "stadium": "新莊棒球場",
        "status": "未開打",
        "batters": {
            3: {"H": 0, "AB": 0, "BB": 0, "HBP": 0, "SAC": 0},
            4: {"H": 0, "AB": 0, "BB": 0, "HBP": 0, "SAC": 0}
        },
        "pitchers": {
            9: {"IP_outs": 0, "balls_total": 0, "strikes": 0, "ER": 0, "K": 0},
            10: {"IP_outs": 0, "balls_total": 0, "strikes": 0, "ER": 0, "K": 0}
        }
    }
]

# ==============================================================================
# 3. 核心運算邏輯 (計算單場與盃賽累積數據)
# ==============================================================================
def get_cumulative_stats():
    """整合歷史基礎數據 + 所有單場比賽數據 = 盃賽總累積數據"""
    batters = {p["id"]: {**CUMULATIVE_BASE_BATTERS.get(p["id"], {"H":0,"AB":0,"BB":0,"HBP":0,"SAC":0})} for p in ALL_PLAYERS if p["type"] == "batter"}
    pitchers = {p["id"]: {**CUMULATIVE_BASE_PITCHERS.get(p["id"], {"IP_outs":0,"balls_total":0,"strikes":0,"ER":0,"K":0})} for p in ALL_PLAYERS if p["type"] == "pitcher"}
    
    # 累加所有單場比賽數值
    for m in matches_db:
        for p_id, stats in m["batters"].items():
            if p_id in batters:
                for k in stats: batters[p_id][k] += stats[k]
        for p_id, stats in m["pitchers"].items():
            if p_id in pitchers:
                for k in stats: pitchers[p_id][k] += stats[k]
                
    # 計算率定公式
    processed_batters = []
    for p in ALL_PLAYERS:
        if p["type"] == "batter":
            b_stat = batters[p["id"]]
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
            p_stat = pitchers[p["id"]]
            outs = p_stat["IP_outs"]
            ip_str = f"{outs // 3}.{outs % 3}"
            era = (p_stat["ER"] * 9) / (outs / 3) if outs > 0 else 0.0
            strike_rate = (p_stat["strikes"] / p_stat["balls_total"] * 100) if p_stat["balls_total"] > 0 else 0.0
            k9 = (p_stat["K"] * 9) / (outs / 3) if outs > 0 else 0.0
            processed_pitchers.append({
                **p, **p_stat, "IP": ip_str, "ERA": f"{era:.2f}",
                "STRIKE_RATE": f"{strike_rate:.1f}%", "K9": f"{k9:.2f}"
            })
            
    return processed_batters, processed_pitchers

# ==============================================================================
# 4. 全域通用網頁外殼 HTML 範本
# ==============================================================================
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>台啤盃 - 聯賽大師管理系統</title>
    <!-- FullCalendar 相關 CDN -->
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
        
        /* 表格專用樣式 */
        .module-title { font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 15px; color: #fff; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; background-color: #151515; }
        th { background-color: #1b7339; color: white; padding: 12px; font-size: 14px; font-weight: bold; text-align: center; }
        td { padding: 14px; text-align: center; border-bottom: 1px solid #2a2a2a; font-size: 15px; color: #fff; }
        tr:hover { background-color: #222; }
        
        /* 表單按鈕與輸入框 */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 15px; }
        .form-control { width: 100%; padding: 10px; background: #2a2a2a; border: 1px solid #444; color: white; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        .btn { padding: 12px 24px; background: #1b7339; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn:hover { background: #228b4c; }
        
        /* 即時按鈕樣式 */
        .btn-group { display: flex; gap: 6px; justify-content: center; }
        .btn-input { padding: 6px 12px; font-size: 12px; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; color: white; }
        .b-h { background-color: #1b7339; } .b-out { background-color: #d93025; } .b-bb { background-color: #1a73e8; } .b-hbp { background-color: #00bcd4; } .b-sac { background-color: #f1a80a; }
        
        /* 行事曆自訂樣式 */
        #calendar { background: #1a1a1a; padding: 20px; border-radius: 8px; color: #fff; border: 1px solid #333; }
        .fc-theme-standard td, .fc-theme-standard th { border: 1px solid #333 !important; }
        .fc-daygrid-day:hover { background-color: #252525; cursor: pointer; }
        .fc-event { background-color: #1b7339 !important; border: 1px solid #2ecc71 !important; color: white !important; padding: 3px; cursor: pointer; font-weight: bold; }
    </style>
</head>
<body>

    <div class="header">
        <h1>🏆 台啤盃棒球聯賽 - 雲端大師整合系統 🏆</h1>
        <p>即時賽程排定、單場即時點擊紀錄房、盃賽數據自動大會串</p>
    </div>

    <div class="nav-tabs">
        <a href="/" class="tab {% if active_tab=='calendar' %}active{% endif %}">🗓️ 台啤盃賽程行事曆</a>
        <a href="/cumulative" class="tab {% if active_tab=='cumulative' %}active{% endif %}">🏆 盃賽累積數據榜</a>
    </div>

    <div class="container">
        <!-- 替換標記 -->
        [[INJECT_CONTENT_HERE]]
    </div>

</body>
</html>
"""

# ==============================================================================
# 5. 路由控制層 (Controllers) - 已修復合併方式
# ==============================================================================

# --- [路由 1]：首頁賽程行事曆檢視與新增
@app.route('/')
def index():
    calendar_content = """
    <!-- 新增賽程功能面板 -->
    <div class="card">
        <h3>➕ 新增台啤盃常規賽程資訊</h3>
        <form method="POST" action="/add-match">
            <div class="form-grid">
                <div>
                    <label style="font-size:14px; color:#aaa;">主場球隊 (一壘側)</label>
                    <select name="team_A" class="form-control" required>
                        {% for team in teams %} <option value="{{ team }}">{{ team }}</option> {% endfor %}
                    </select>
                </div>
                <div>
                    <label style="font-size:14px; color:#aaa;">客場球隊 (三壘側)</label>
                    <select name="team_B" class="form-control" required>
                        {% for team in teams %} <option value="{{ team }}">{{ team }}</option> {% endfor %}
                    </select>
                </div>
                <div>
                    <label style="font-size:14px; color:#aaa;">比賽日期</label>
                    <input type="date" name="date" class="form-control" required>
                </div>
                <div>
                    <label style="font-size:14px; color:#aaa;">開打時間</label>
                    <input type="time" name="time" class="form-control" required>
                </div>
                <div>
                    <label style="font-size:14px; color:#aaa;">比賽球場</label>
                    <input type="text" name="stadium" class="form-control" placeholder="例如：天母棒球場" required>
                </div>
            </div>
            <button type="submit" class="btn">確認排定並整合至行事曆</button>
        </form>
    </div>

    <!-- 彙整行事曆區塊 -->
    <div class="card">
        <h3 style="margin-top:0; color:#2ecc71;">🗓️ 台啤盃大會官方時程行事曆 (點擊任一場賽事直接切入單場即時紀錄房)</h3>
        <p style="color:#aaa; font-size:14px; margin-bottom:20px;">💡 指引：下方行事曆會同步彙整所有排定的對戰。直接點選行事曆內的比賽區塊，即可進入動態點擊面板！</p>
        <div id="calendar"></div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var calendarEl = document.getElementById('calendar');
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'dayGridMonth',
                locale: 'zh-tw',
                editable: false,
                events: [
                    {% for m in matches %}
                    {
                        id: '{{ m.id }}',
                        title: '{{ m.team_A }} VS {{ m.team_B }} ({{ m.stadium }})',
                        start: '{{ m.date }}T{{ m.time }}',
                        url: '/match/{{ m.id }}' // 點擊直接路由到該場次的即時紀錄房
                    },
                    {% endfor %}
                ]
            });
            calendar.render();
        });
    </script>
    """
    # 將內容安全注入 BASE_TEMPLATE 中
    full_html = BASE_TEMPLATE.replace('[[INJECT_CONTENT_HERE]]', calendar_content)
    return render_template_string(full_html, active_tab='calendar', teams=TEAMS, matches=matches_db)


# --- [動作路由]：接收表單資料，動態新增賽程
@app.route('/add-match', methods=['POST'])
def add_match():
    team_a = request.form.get('team_A')
    team_b = request.form.get('team_B')
    date = request.form.get('date')
    time = request.form.get('time')
    stadium = request.form.get('stadium')
    
    new_id = len(matches_db) + 1
    
    # 建立新賽事，並自動抓取屬於這兩隊的球員初始化單場 Box Score 欄位
    match_batters = {}
    match_pitchers = {}
    for p in ALL_PLAYERS:
        if p["team"] in [team_a, team_b]:
            if p["type"] == "batter":
                match_batters[p["id"]] = {"H": 0, "AB": 0, "BB": 0, "HBP": 0, "SAC": 0}
            elif p["type"] == "pitcher":
                match_pitchers[p["id"]] = {"IP_outs": 0, "balls_total": 0, "strikes": 0, "ER": 0, "K": 0}
                
    matches_db.append({
        "id": new_id, "team_A": team_a, "team_B": team_b,
        "date": date, "time": time, "stadium": stadium, "status": "未開打",
        "batters": match_batters, "pitchers": match_pitchers
    })
    return redirect(url_for('index'))


# --- [路由 2]：盃賽累積數據榜檢視
@app.route('/cumulative')
def cumulative():
    c_batters, c_pitchers = get_cumulative_stats()
    cumulative_content = """
    <div class="card">
        <div class="module-title">🏆 盃賽生涯大會累積榜 - 打者數據 (Batting Module)</div>
        <p style="color:#aaa; font-size:13px; text-align:center;">（數據流已完美整合：歷史底線數據 + 所有單場動態點擊數值的即時加總）</p>
        <table>
            <thead>
                <tr>
                    <th>球員</th><th>背號</th><th>球隊</th><th>守備位置</th>
                    <th>打席(PA)</th><th>打數(AB)</th><th>安打(H)</th><th>四壞(BB)</th><th>觸身(HBP)</th><th>犧牲(SAC)</th>
                    <th style="color:#2ecc71;">打擊率(AVG)</th><th style="color:#3498db;">上壘率(OBP)</th>
                </tr>
            </thead>
            <tbody>
                {% for p in batters %}
                <tr>
                    <td><strong>{{ p.name }}</strong></td><td>#{{ p.number }}</td><td>{{ p.team }}</td><td>{{ p.position }}</td>
                    <td>{{ p.PA }}</td><td>{{ p.AB }}</td><td>{{ p.H }}</td><td>{{ p.BB }}</td><td>{{ p.HBP }}</td><td>{{ p.SAC }}</td>
                    <td style="color:#2ecc71; font-weight:bold;">{{ p.AVG }}</td><td style="color:#3498db; font-weight:bold;">{{ p.OBP }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="card">
        <div class="module-title">🏆 盃賽生涯大會累積榜 - 投手數據 (Pitching Module)</div>
        <table>
            <thead>
                <tr>
                    <th>球員</th><th>背號</th><th>球隊</th><th>局數(IP)</th><th>總球數</th><th>好球數</th><th>自責分(ER)</th><th>奪三振(K)</th>
                    <th style="color:#2ecc71;">防禦率(ERA)</th><th>好球率</th><th>K/9 值</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pitchers %}
                <tr>
                    <td><strong>{{ p.name }}</strong></td><td>#{{ p.number }}</td><td>{{ p.team }}</td>
                    <td>{{ p.IP }}</td><td>{{ p.balls_total }}</td><td>{{ p.strikes }}</td><td>{{ p.ER }}</td><td>{{ p.K }}</td>
                    <td style="color:#2ecc71; font-weight:bold;">{{ p.ERA }}</td><td>{{ p.STRIKE_RATE }}</td><td>{{ p.K9 }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    """
    full_html = BASE_TEMPLATE.replace('[[INJECT_CONTENT_HERE]]', cumulative_content)
    return render_template_string(full_html, active_tab='cumulative', batters=c_batters, pitchers=c_pitchers)


# --- [路由 3]：單場即時紀錄房 (由行事曆點入對應 ID)
@app.route('/match/<int:match_id>')
def match_room(match_id):
    # 抓取特定賽事
    match = next((m for m in matches_db if m["id"] == match_id), None)
    if not match:
        return "賽事不存在", 404
        
    # 過濾出參與此場比賽的兩隊選手名單，傳遞給前端動態生成點擊行
    m_batters = []
    m_pitchers = []
    for p in ALL_PLAYERS:
        if p["team"] in [match["team_A"], match["team_B"]]:
            if p["type"] == "batter":
                if p["id"] not in match["batters"]:
                    match["batters"][p["id"]] = {"H":0,"AB":0,"BB":0,"HBP":0,"SAC":0}
                m_batters.append({**p, **match["batters"][p["id"]]})
            elif p["type"] == "pitcher":
                if p["id"] not in match["pitchers"]:
                    match["pitchers"][p["id"]] = {"IP_outs":0,"balls_total":0,"strikes":0,"ER":0,"K":0}
                m_pitchers.append({**p, **match["pitchers"][p["id"]]})

    match_template = """
    <div class="card" style="background: linear-gradient(to right, #151515, #1b3827); border-left: 6px solid #2ecc71;">
        <span style="background:#d93025; padding:4px 8px; border-radius:4px; font-size:12px; font-weight:bold;">單場 LIVE 紀錄房</span>
        <h2 style="margin: 10px 0 5px 0;">🏟️ 戰場：{{ match.stadium }} ({{ match.date }} {{ match.time }})</h2>
        <div style="display:flex; gap:30px; font-size:24px; font-weight:bold; margin-top:15px; align-items:center;">
            <div style="color:#2ecc71;">{{ match.team_A }} (主)</div>
            <div style="color:#555;">VS</div>
            <div style="color:#f1a80a;">{{ match.team_B }} (客)</div>
        </div>
        <a href="/" style="display:inline-block; margin-top:20px; color:#aaa; text-decoration:none;">⬅️ 回到排定行事曆</a>
    </div>

    <!-- 單場打者點擊輸入面板 -->
    <div class="card">
        <div class="module-title">🏏 【本場專屬】打者即時輸入面板 (Batting Box Score)</div>
        <table>
            <thead>
                <tr>
                    <th>球員</th><th>球隊</th><th>守備位置</th><th>打席(PA)</th><th>打數(AB)</th><th>安打(H)</th><th>四壞(BB)</th><th>觸身(HBP)</th><th>犧牲(SAC)</th><th>單場AVG</th>
                    <th style="width:30%;">紀錄員即時輸入動作條</th>
                </tr>
            </thead>
            <tbody>
                {% for p in batters %}
                <tr id="b-row-{{ p.id }}">
                    <td><strong>{{ p.name }}</strong></td><td>{{ p.team }}</td><td><span style="background:#2d2d2d; padding:2px 6px; border-radius:4px;">{{ p.position }}</span></td>
                    <td id="b-pa-{{ p.id }}">0</td><td id="b-ab-{{ p.id }}">{{ p.AB }}</td><td id="b-h-{{ p.id }}">{{ p.H }}</td><td id="b-bb-{{ p.id }}">{{ p.BB }}</td><td id="b-hbp-{{ p.id }}">{{ p.HBP }}</td><td id="b-sac-{{ p.id }}">{{ p.SAC }}</td>
                    <td id="b-avg-{{ p.id }}" style="color:#2ecc71; font-weight:bold;">.000</td>
                    <td>
                        <div class="btn-group">
                            <button class="btn-input b-h" onclick="sendAction({{ match.id }}, 'batter', {{ p.id }}, 'H')">H</button>
                            <button class="btn-input b-out" onclick="sendAction({{ match.id }}, 'batter', {{ p.id }}, 'OUT')">OUT</button>
                            <button class="btn-input b-bb" onclick="sendAction({{ match.id }}, 'batter', {{ p.id }}, 'BB')">BB</button>
                            <button class="btn-input b-hbp" onclick="sendAction({{ match.id }}, 'batter', {{ p.id }}, 'HBP')">HBP</button>
                            <button class="btn-input b-sac" onclick="sendAction({{ match.id }}, 'batter', {{ p.id }}, 'SAC')">SAC</button>
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- 單場投手點擊輸入面板 -->
    <div class="card">
        <div class="module-title">⚾ 【本場專屬】投手即時輸入面板 (Pitching Box Score)</div>
        <table>
            <thead>
                <tr>
                    <th>球員</th><th>球隊</th><th>局數(IP)</th><th>總球數</th><th>好球數</th><th>自責分(ER)</th><th>奪三振(K)</th><th>單場ERA</th><th>好球率</th>
                    <th style="width:30%;">紀錄員即時輸入動作條</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pitchers %}
                <tr id="p-row-{{ p.id }}">
                    <td><strong>{{ p.name }}</strong></td><td>{{ p.team }}</td>
                    <td id="p-ip-{{ p.id }}">0.0</td><td id="p-total-{{ p.id }}">{{ p.balls_total }}</td><td id="p-strikes-{{ p.id }}">{{ p.strikes }}</td><td id="p-er-{{ p.id }}">{{ p.ER }}</td><td id="p-k-{{ p.id }}">{{ p.K }}</td>
                    <td id="p-era-{{ p.id }}" style="color:#2ecc71; font-weight:bold;">0.00</td><td id="p-rate-{{ p.id }}">0%</td>
                    <td>
                        <div class="btn-group">
                            <button class="btn-input b-h" style="background:#1b7339;" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'STRIKE')">好球</button>
                            <button class="btn-input b-bb" style="background:#1a73e8;" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'BALL')">壞球</button>
                            <button class="btn-input b-out" style="background:#d93025;" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'OUT')">出局</button>
                            <button class="btn-input b-sac" style="background:#f1a80a;" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'ER')">失分</button>
                            <button class="btn-input b-hbp" style="background:#009688;" onclick="sendAction({{ match.id }}, 'pitcher', {{ p.id }}, 'K')">三振</button>
                        </div>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <script>
        // 後端資料即時在前端同步
        const batters = { {% for p in batters %} "{{ p.id }}": { h: {{ p.H }}, ab: {{ p.AB }}, bb: {{ p.BB }}, hbp: {{ p.HBP }}, sac: {{ p.SAC }} }, {% endfor %} };
        const pitchers = { {% for p in pitchers %} "{{ p.id }}": { outs: {{ p.IP_outs }}, total: {{ p.balls_total }}, strikes: {{ p.strikes }}, er: {{ p.ER }}, k: {{ p.K }} }, {% endfor %} };

        function runCalcBatter(id) {
            let b = batters[id];
            let pa = b.ab + b.bb + b.hbp + b.sac;
            let avg = b.ab > 0 ? (b.h / b.ab) : 0;
            document.getElementById(`b-pa-${id}`).innerText = pa;
            document.getElementById(`b-ab-${id}`).innerText = b.ab;
            document.getElementById(`b-h-${id}`).innerText = b.h;
            document.getElementById(`b-bb-${id}`).innerText = b.bb;
            document.getElementById(`b-hbp-${id}`).innerText = b.hbp;
            document.getElementById(`b-sac-${id}`).innerText = b.sac;
            document.getElementById(`b-avg-${id}`).innerText = avg === 1 ? "1.000" : avg.toFixed(3).substring(1);
        }

        function runCalcPitcher(id) {
            let p = pitchers[id];
            let ipStr = `${Math.floor(p.outs / 3)}.${p.outs % 3}`;
            let era = p.outs > 0 ? ((p.er * 9) / (p.outs / 3)) : 0;
            let rate = p.total > 0 ? ((p.strikes / p.total) * 100) : 0;
            document.getElementById(`p-ip-${id}`).innerText = ipStr;
            document.getElementById(`p-total-${id}`).innerText = p.total;
            document.getElementById(`p-strikes-${id}`).innerText = p.strikes;
            document.getElementById(`p-er-${id}`).innerText = p.er;
            document.getElementById(`p-k-${id}`).innerText = p.k;
            document.getElementById(`p-era-${id}`).innerText = era.toFixed(2);
            document.getElementById(`p-rate-${id}`).innerText = rate.toFixed(1) + "%";
        }

        // 使用非同步 AJAX 向後端傳遞紀錄變更，保證重新整理網頁時單場紀錄依舊留存
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
                        batters[pId] = data.new_data;
                        runCalcBatter(pId);
                    } else {
                        pitchers[pId] = data.new_data;
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
    full_html = BASE_TEMPLATE.replace('[[INJECT_CONTENT_HERE]]', match_template)
    return render_template_string(full_html, active_tab='calendar', match=match, batters=m_batters, pitchers=m_pitchers)


# --- [API 路由]：非同步處理前端點擊事件並同步回後端記憶體數據庫
@app.route('/api/update-record', methods=['POST'])
def api_update_record():
    data = request.json
    m_id = data.get("match_id")
    p_type = data.get("player_type")
    p_id = int(data.get("player_id"))
    action = data.get("action_type")
    
    match = next((m for m in matches_db if m["id"] == m_id), None)
    if not match:
        return jsonify({"success": False, "msg": "Match not found"})
        
    if p_type == "batter":
        p_stat = match["batters"].setdefault(p_id, {"H": 0, "AB": 0, "BB": 0, "HBP": 0, "SAC": 0})
        if action == "H":
            p_stat["H"] += 1
            p_stat["AB"] += 1
        elif action == "OUT":
            p_stat["AB"] += 1
        elif action == "BB":
            p_stat["BB"] += 1
        elif action == "HBP":
            p_stat["HBP"] += 1
        elif action == "SAC":
            p_stat["SAC"] += 1
        return jsonify({"success": True, "new_data": p_stat})
        
    elif p_type == "pitcher":
        p_stat = match["pitchers"].setdefault(p_id, {"IP_outs": 0, "balls_total": 0, "strikes": 0, "ER": 0, "K": 0})
        if action == "STRIKE":
            p_stat["strikes"] += 1
            p_stat["balls_total"] += 1
        elif action == "BALL":
            p_stat["balls_total"] += 1
        elif action == "OUT":
            p_stat["IP_outs"] += 1
            p_stat["strikes"] += 1
            p_stat["balls_total"] += 1
        elif action == "ER":
            p_stat["ER"] += 1
        elif action == "K":
            p_stat["K"] += 1
            p_stat["IP_outs"] += 1
            p_stat["strikes"] += 1
            p_stat["balls_total"] += 1
        return jsonify({"success": True, "new_data": p_stat})

    return jsonify({"success": False})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)