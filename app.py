from flask import Flask, render_template_string, request
import os

app = Flask(__name__)

# ==============================================================================
# 1. 數據庫結構 - 台啤盃六大勁旅 & 小系列球員基本初始數據
# ==============================================================================
batters_init = [
    {"id": 1, "number": "1", "name": "王小明", "team": "台灣啤酒", "position": "游擊手", "H": 5, "AB": 15, "BB": 2, "HBP": 1, "SAC": 1},
    {"id": 2, "number": "7", "name": "陳小同", "team": "台北市大", "position": "中外野手", "H": 2, "AB": 10, "BB": 4, "HBP": 0, "SAC": 0},
    {"id": 3, "number": "18", "name": "張小豪", "team": "台灣運彩", "position": "指定打擊", "H": 6, "AB": 12, "BB": 3, "HBP": 1, "SAC": 0},
    {"id": 4, "number": "31", "name": "林小華", "team": "台南市", "position": "一壘手", "H": 3, "AB": 11, "BB": 2, "HBP": 0, "SAC": 1},
    {"id": 5, "number": "52", "name": "黃小鋒", "team": "全越運動", "position": "左外野手", "H": 4, "AB": 14, "BB": 1, "HBP": 1, "SAC": 0},
    {"id": 6, "number": "66", "name": "賴小宇", "team": "桃園市", "position": "捕手", "H": 2, "AB": 9, "BB": 2, "HBP": 0, "SAC": 2}
]

pitchers_init = [
    {"id": 1, "name": "林投手", "team": "台灣啤酒", "IP_outs": 16, "balls_total": 88, "strikes": 58, "ER": 3, "K": 6}, # 16 outs = 5.1 局
    {"id": 2, "name": "黃終結", "team": "台北市大", "IP_outs": 3, "balls_total": 15, "strikes": 11, "ER": 0, "K": 2},  # 3 outs = 1.0 局
    {"id": 3, "name": "張小投", "team": "台灣運彩", "IP_outs": 15, "balls_total": 75, "strikes": 48, "ER": 2, "K": 4},
    {"id": 4, "name": "陳小投", "team": "台南市", "IP_outs": 12, "balls_total": 60, "strikes": 38, "ER": 4, "K": 3}
]

today_match = {
    "team_A": "台灣啤酒",
    "team_B": "台北市大",
    "time": "18:30",
    "stadium": "天母棒球場",
    "weather": "晴朗 29°C"
}

# ==============================================================================
# 2. 展示層 (HTML 介面 - 完美復刻動態點擊面板，移除純文字跑馬燈)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>台啤盃 - 紀錄員即時輸入數據面板</title>
    <style>
        body { font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 0; background-color: #1a1a1a; color: #e0e0e0; }
        .header { background: linear-gradient(135deg, #0d5c3a, #11422c); color: white; padding: 20px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
        .nav-tabs { display: flex; justify-content: center; background: #222; border-bottom: 2px solid #0d5c3a; margin-bottom: 20px; }
        .tab { padding: 15px 30px; cursor: pointer; font-weight: bold; color: #aaa; text-decoration: none; border-bottom: 3px solid transparent; }
        .tab:hover, .tab.active { color: #2ecc71; border-bottom: 3px solid #2ecc71; background: #2d2d2d; }
        .container { max-width: 1300px; margin: 0 auto; padding: 20px; }
        .card { background: #262626; border-radius: 10px; padding: 25px; box-shadow: 0 6px 12px rgba(0,0,0,0.2); margin-bottom: 25px; }
        .search-box { width: 100%; max-width: 500px; padding: 12px; font-size: 16px; background: #333; color: #fff; border: 1px solid #444; border-radius: 6px; margin-bottom: 20px; }
        
        /* 復刻截圖的綠色表格標題與黑底風格 */
        .module-title { font-size: 22px; font-weight: bold; text-align: center; margin-bottom: 15px; color: #ffffff; display: flex; align-items: center; justify-content: center; gap: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; background-color: #1e1e1e; }
        th { background-color: #1b7339; color: white; padding: 12px 8px; font-size: 14px; font-weight: normal; }
        td { padding: 14px 8px; text-align: center; border-bottom: 1px solid #333; font-size: 15px; color: #fff; }
        tr:hover { background-color: #282828; }
        
        /* 即時紀錄輸入按鈕樣式 */
        .btn-group { display: flex; gap: 6px; justify-content: center; flex-wrap: wrap; }
        .btn-input { padding: 5px 10px; font-size: 12px; font-weight: bold; border: none; border-radius: 4px; cursor: pointer; color: white; transition: transform 0.1s; }
        .btn-input:active { transform: scale(0.9); }
        
        /* 打者按鈕顏色 */
        .b-h { background-color: #1b7339; }    /* 安打綠 */
        .b-out { background-color: #d93025; }  /* 出局紅 */
        .b-bb { background-color: #1a73e8; }   /* 保送藍 */
        .b-hbp { background-color: #00bcd4; }  /* 觸身青 */
        .b-sac { background-color: #f1a80a; }  /* 犧牲橘 */
        
        /* 投手按鈕顏色 */
        .p-strike { background-color: #1b7339; }
        .p-ball { background-color: #1a73e8; }
        .p-out { background-color: #d93025; }
        .p-er { background-color: #f1a80a; }
        .p-k { background-color: #009688; }
        
        .btn-search { padding: 12px 20px; font-size: 16px; background: #1b7339; color: white; border: none; border-radius: 6px; margin-left: 10px; cursor: pointer; }
    </style>
</head>
<body>

    <div class="header">
        <h1>🏆 台啤盃全國棒球菁英賽 - 轉播即時數據系統 🏆</h1>
        <p>六大勁旅官方即時整合面板（台灣啤酒、台北市大、台灣運彩、台南市、全越運動、桃園市）</p>
    </div>

    <div class="nav-tabs">
        <a href="/" class="tab {% if active_tab=='home' %}active{% endif %}">🏏 紀錄員即時輸入面板</a>
        <a href="/match" class="tab {% if active_tab=='match' %}active{% endif %}">📺 今日賽事整合</a>
    </div>

    <div class="container">
        
        {% if active_tab == 'home' %}
        <!-- 搜尋功能 -->
        <div class="card">
            <h2>🔍 台啤盃球員快速篩選</h2>
            <form method="GET" action="/">
                <input type="text" name="q" class="search-box" placeholder="搜尋球員姓名、球隊..." value="{{ query }}">
                <button type="submit" class="btn-search">篩選</button>
                {% if query %}<a href="/" style="margin-left:10px; color:#aaa; text-decoration:none;">[清除條件]</a>{% endif %}
            </form>
        </div>

        <!-- 打者數據榜 (Batting Module) -->
        <div class="card">
            <div class="module-title">🏏 打者數據榜 (Batting Module)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 8%;">球員</th>
                        <th style="width: 10%;">球隊</th>
                        <th>打席(PA)</th>
                        <th>打數(AB)</th>
                        <th>安打(H)</th>
                        <th>四壞(BB)</th>
                        <th>觸身(HBP)</th>
                        <th>犧牲(SAC)</th>
                        <th>打擊率(AVG)</th>
                        <th>上壘率(OBP)</th>
                        <th style="width: 32%;">紀錄員即時輸入面板</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in b_players %}
                    <tr id="batter-row-{{ p.id }}">
                        <td style="font-weight: bold; color: #fff;">{{ p.name }}</td>
                        <td style="color: #aaa;">{{ p.team }}</td>
                        <td id="b-pa-{{ p.id }}">0</td>
                        <td id="b-ab-{{ p.id }}">{{ p.AB }}</td>
                        <td id="b-h-{{ p.id }}">{{ p.H }}</td>
                        <td id="b-bb-{{ p.id }}">{{ p.BB }}</td>
                        <td id="b-hbp-{{ p.id }}">{{ p.HBP }}</td>
                        <td id="b-sac-{{ p.id }}">{{ p.SAC }}</td>
                        <td id="b-avg-{{ p.id }}" style="color: #2ecc71; font-weight: bold;">.000</td>
                        <td id="b-obp-{{ p.id }}" style="color: #3498db; font-weight: bold;">.000</td>
                        <td>
                            <div class="btn-group">
                                <button class="btn-input b-h" onclick="updateBatter({{ p.id }}, 'H')">H (安打)</button>
                                <button class="btn-input b-out" onclick="updateBatter({{ p.id }}, 'OUT')">OUT (出局)</button>
                                <button class="btn-input b-bb" onclick="updateBatter({{ p.id }}, 'BB')">BB (保送)</button>
                                <button class="btn-input b-hbp" onclick="updateBatter({{ p.id }}, 'HBP')">HBP (觸身)</button>
                                <button class="btn-input b-sac" onclick="updateBatter({{ p.id }}, 'SAC')">SAC (犧牲)</button>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 投手數據榜 (Pitching Module) -->
        <div class="card">
            <div class="module-title">⚾ 投手數據榜 (Pitching Module)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 8%;">球員</th>
                        <th style="width: 10%;">球隊</th>
                        <th>局數(IP)</th>
                        <th>總球數</th>
                        <th>好球數</th>
                        <th>自責分(ER)</th>
                        <th>奪三振(K)</th>
                        <th>防禦率(ERA)</th>
                        <th>好球率</th>
                        <th>K/9 值</th>
                        <th style="width: 32%;">紀錄員即時輸入面板</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in p_players %}
                    <tr id="pitcher-row-{{ p.id }}">
                        <td style="font-weight: bold; color: #fff;">{{ p.name }}</td>
                        <td style="color: #aaa;">{{ p.team }}</td>
                        <td id="p-ip-{{ p.id }}">0.0</td>
                        <td id="p-total-{{ p.id }}">{{ p.balls_total }}</td>
                        <td id="p-strikes-{{ p.id }}">{{ p.strikes }}</td>
                        <td id="p-er-{{ p.id }}">{{ p.ER }}</td>
                        <td id="p-k-{{ p.id }}">{{ p.K }}</td>
                        <td id="p-era-{{ p.id }}" style="color: #2ecc71; font-weight: bold;">0.00</td>
                        <td id="p-rate-{{ p.id }}">0.0%</td>
                        <td id="p-k9-{{ p.id }}">0.00</td>
                        <td>
                            <div class="btn-group">
                                <button class="btn-input p-strike" onclick="updatePitcher({{ p.id }}, 'STRIKE')">好球 (Strike)</button>
                                <button class="btn-input p-ball" onclick="updatePitcher({{ p.id }}, 'BALL')">壞球 (Ball)</button>
                                <button class="btn-input p-out" onclick="updatePitcher({{ p.id }}, 'OUT')">抓到出局 (Out)</button>
                                <button class="btn-input p-er" onclick="updatePitcher({{ p.id }}, 'ER')">失自責分 (ER)</button>
                                <button class="btn-input p-k" onclick="updatePitcher({{ p.id }}, 'K')">奪三振 (K)</button>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <!-- 互動連動核心運算 JavaScript -->
        <script>
            // 初始打者結構轉移至JS
            const batters = {
                {% for p in b_players %}
                "{{ p.id }}": { h: {{ p.H }}, ab: {{ p.AB }}, bb: {{ p.BB }}, hbp: {{ p.HBP }}, sac: {{ p.SAC }} },
                {% endfor %}
            };

            // 初始投手結構轉移至JS
            const pitchers = {
                {% for p in p_players %}
                "{{ p.id }}": { outs: {{ p.IP_outs }}, total: {{ p.balls_total }}, strikes: {{ p.strikes }}, er: {{ p.ER }}, k: {{ p.K }} },
                {% endfor %}
            };

            // 重新計算打者所有連動公式
            function calcBatter(id) {
                let b = batters[id];
                let pa = b.ab + b.bb + b.hbp + b.sac;
                let avg = b.ab > 0 ? (b.h / b.ab) : 0;
                let obp = pa > 0 ? ((b.h + b.bb + b.hbp) / pa) : 0;

                document.getElementById(`b-pa-${id}`).innerText = pa;
                document.getElementById(`b-ab-${id}`).innerText = b.ab;
                document.getElementById(`b-h-${id}`).innerText = b.h;
                document.getElementById(`b-bb-${id}`).innerText = b.bb;
                document.getElementById(`b-hbp-${id}`).innerText = b.hbp;
                document.getElementById(`b-sac-${id}`).innerText = b.sac;
                
                document.getElementById(`b-avg-${id}`).innerText = avg === 1 ? "1.000" : avg.toFixed(3).substring(1);
                document.getElementById(`b-obp-${id}`).innerText = obp === 1 ? "1.000" : obp.toFixed(3).substring(1);
            }

            // 重新計算投手所有連動公式
            function calcPitcher(id) {
                let p = pitchers[id];
                
                // 算出局數顯示 (例如 16個出局數 = 5局又1個出局數 = 5.1)
                let fullInnings = Math.floor(p.outs / 3);
                let remainingOuts = p.outs % 3;
                let ipStr = `${fullInnings}.${remainingOuts}`;
                
                // ERA 公式 = (ER * 9) / (outs / 3)
                let inningsCount = p.outs / 3;
                let era = inningsCount > 0 ? ((p.er * 9) / inningsCount) : 0;
                
                // 好球率
                let strikeRate = p.total > 0 ? ((p.strikes / p.total) * 100) : 0;
                
                // K/9 值 = (K * 9) / (outs / 3)
                let k9 = inningsCount > 0 ? ((p.k * 9) / inningsCount) : 0;

                document.getElementById(`p-ip-${id}`).innerText = ipStr;
                document.getElementById(`p-total-${id}`).innerText = p.total;
                document.getElementById(`p-strikes-${id}`).innerText = p.strikes;
                document.getElementById(`p-er-${id}`).innerText = p.er;
                document.getElementById(`p-k-${id}`).innerText = p.k;
                
                document.getElementById(`p-era-${id}`).innerText = era.toFixed(2);
                document.getElementById(`p-rate-${id}`).innerText = strikeRate.toFixed(1) + "%";
                document.getElementById(`p-k9-${id}`).innerText = k9.toFixed(2);
            }

            // 打者點擊動作觸發
            function updateBatter(id, type) {
                if (type === 'H') {
                    batters[id].h += 1;
                    batters[id].ab += 1;
                } else if (type === 'OUT') {
                    batters[id].ab += 1;
                } else if (type === 'BB') {
                    batters[id].bb += 1;
                } else if (type === 'HBP') {
                    batters[id].hbp += 1;
                } else if (type === 'SAC') {
                    batters[id].sac += 1;
                }
                calcBatter(id);
            }

            // 投手點擊動作觸發
            function updatePitcher(id, type) {
                if (type === 'STRIKE') {
                    pitchers[id].strikes += 1;
                    pitchers[id].total += 1;
                } else if (type === 'BALL') {
                    pitchers[id].total += 1;
                } else if (type === 'OUT') {
                    pitchers[id].outs += 1;
                    pitchers[id].strikes += 1; // 抓到出局通常伴隨好球球數增加
                    pitchers[id].total += 1;
                } else if (type === 'ER') {
                    pitchers[id].er += 1;
                } else if (type === 'K') {
                    pitchers[id].k += 1;
                    pitchers[id].outs += 1; // 三振直接拿到一個出局數
                    pitchers[id].strikes += 1;
                    pitchers[id].total += 1;
                }
                calcPitcher(id);
            }

            // 頁面加載完成後自動初始化所有球員數值
            window.onload = function() {
                Object.keys(batters).forEach(id => calcBatter(id));
                Object.keys(pitchers).forEach(id => calcPitcher(id));
            };
        </script>
        {% endif %}

        {% if active_tab == 'match' %}
        <div class="card" style="background: #222; border-left: 6px solid #1b7339;">
            <h2>📺 台啤盃今日賽事轉播面板</h2>
            <p style="font-size: 18px;">🏟️ <strong>今日戰場：</strong> {{ match_info.stadium }} | 🕒 預計開打：{{ match_info.time }} | ☀️ 氣象狀況：{{ match_info.weather }}</p>
            <div style="display: flex; justify-content: space-around; align-items: center; margin-top: 30px;">
                <div style="text-align: center;">
                    <h3 style="font-size: 28px; color: #2ecc71; margin:0;">{{ match_info.team_A }}</h3>
                    <p style="color:#888;">(主場一壘側)</p>
                </div>
                <div style="font-size: 24px; font-weight: bold; color: #555;">VS</div>
                <div style="text-align: center;">
                    <h3 style="font-size: 28px; color: #f1a80a; margin:0;">{{ match_info.team_B }}</h3>
                    <p style="color:#888;">(客場三壘側)</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h3>🔥 今日對戰焦點隊伍陣容 (台灣啤酒 & 台北市大)</h3>
            <p style="color: #aaa; font-size: 14px;">提示：請至「紀錄員即時輸入面板」點選按鈕，進行即時戰況連動調度。</p>
        </div>
        {% endif %}

    </div>

</body>
</html>
"""

# ==============================================================================
# 3. 路由控制層 (過濾搜尋結果)
# ==============================================================================
@app.route('/')
def home():
    query = request.args.get('q', '')
    
    # 依搜尋條件過濾打者與投手
    if query:
        b_filtered = [b for b in batters_init if query.lower() in b["name"].lower() or query.lower() in b["team"].lower()]
        p_filtered = [p for p in pitchers_init if query.lower() in p["name"].lower() or query.lower() in p["team"].lower()]
    else:
        b_filtered = batters_init
        p_filtered = pitchers_init
        
    return render_template_string(HTML_TEMPLATE, active_tab='home', b_players=b_filtered, p_players=p_filtered, query=query)

@app.route('/match')
def match():
    return render_template_string(HTML_TEMPLATE, active_tab='match', match_info=today_match)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)