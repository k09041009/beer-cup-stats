from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

# ==============================================================================
# 1. 數據庫結構 - 台灣爆米花聯賽六大隊伍 & 小字輩系列球員
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

today_match = {
    "team_A": "台灣啤酒",
    "team_B": "台北市大",
    "time": "18:30",
    "stadium": "天母棒球場",
    "weather": "晴朗 29°C"
}

# ==============================================================================
# 2. 核心運算邏輯
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
# 3. HTML 介面與排版 (確保無多餘引號干擾)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>爆米花聯盟等級 - 轉播即時文字導播系統</title>
    <style>
        body { font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 0; background-color: #f0f2f5; color: #333; }
        .header { background: linear-gradient(135deg, #0d5c3a, #063621); color: white; padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
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
    </style>
</head>
<body>

    <div class="header">
        <h1>⚾ 台灣頂級業餘聯賽 - 專業轉播數據系統 ⚾</h1>
        <p>六大勁旅戰力整合面板（台灣啤酒、台北市大、台灣運彩、台南市、全越運動、桃園市）</p>
    </div>

    <div class="nav-tabs">
        <a href="/" class="tab {% if active_tab=='home' %}active{% endif %}">🏏 球員名冊與搜尋</a>
        <a href="/leaderboard" class="tab {% if active_tab=='leader' %}active{% endif %}">🏆 數據排行榜</a>
        <a href="/match" class="tab {% if active_tab=='match' %}active{% endif %}">📺 今日賽事整合</a>
    </div>

    <div class="container">
        
        {% if active_tab == 'home' %}
        <div class="card">
            <h2>🔍 球員快速搜尋機制</h2>
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
        <h2>🏆 聯賽個人數據領先榜 (打擊三冠王)</h2>
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
            <h2>📺 今日賽事轉播資訊整合面板</h2>
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
        
        <div class="card">
            <h3>🔥 兩隊焦點球員近況變化（主播播報專用素材）</h3>
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
# 4. 路由與網頁控制層
# ==============================================================================
@app.route('/')
def home():
    query = request.args.get('q', '')
    players = process_data(search_query=query)
    return render_template_string(HTML_TEMPLATE, active_tab='home', players=players, query=query)

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
    return render_template_string(HTML_TEMPLATE, active_tab='match', players=players, match_info=today_match)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)