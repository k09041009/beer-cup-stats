from flask import Flask, render_template_string, redirect, url_for

app = Flask(__name__)

# ==============================================================================
# 3. 數據庫結構構想 (Data Schema) - 在 Python 中以 Dict 陣列呈現原始紀錄
# ==============================================================================

# 打者資料庫：紀錄最原始的事件，不手動算 AVG
batters_db = [
    {"id": 1, "name": "王小明", "team": "台啤一隊", "H": 5, "AB": 15, "BB": 2, "HBP": 1, "SAC": 1},
    {"id": 2, "name": "陳大同", "team": "台啤一隊", "H": 2, "AB": 10, "BB": 4, "HBP": 0, "SAC": 0}
]

# 投手資料庫：依構想紀錄「總出局數 (total_outs)」，不紀錄不精確的浮點數局數
pitchers_db = [
    {"id": 1, "name": "林投手", "team": "台啤一隊", "ER": 3, "total_outs": 16, "pitches": 85, "strikes": 55, "K": 6}, # 16個出局數 = 5.1局
    {"id": 2, "name": "黃終結", "team": "台啤二隊", "ER": 0, "total_outs": 3, "pitches": 15, "strikes": 11, "K": 2}   # 3個出局數 = 1.0局
]


# ==============================================================================
# 2. 運算層 (Core Logic Formulas)
# ==============================================================================

def calculate_batting_stats(b):
    """計算打者數據：包含 AVG 格式化、以及 OBP (上壘率)"""
    h, ab, bb, hbp, sac = b["H"], b["AB"], b["BB"], b["HBP"], b["SAC"]
    
    # PA (打席) = AB + BB + HBP + SAC
    pa = ab + bb + hbp + sac
    
    # 1. 打擊率 AVG = H / AB
    avg = (h / ab) if ab > 0 else 0.0
    avg_str = f"{avg:.3f}".lstrip('0') if avg < 1.0 else f"{avg:.3f}"
    if avg_str == ".": avg_str = ".000"
    
    # 2. 上壘率 OBP = (H + BB + HBP) / (AB + BB + HBP + SAC)
    obp = (h + bb + hbp) / pa if pa > 0 else 0.0
    obp_str = f"{obp:.3f}".lstrip('0') if obp < 1.0 else f"{obp:.3f}"
    if obp_str == ".": obp_str = ".000"
    
    return {"pa": pa, "avg": avg_str, "obp": obp_str}


def calculate_pitching_stats(p):
    """計算投手數據：符合總出局數轉換「.1, .2」格式、ERA以9局為基準、好球率、K/9"""
    er, total_outs, pitches, strikes, k = p["ER"], p["total_outs"], p["pitches"], p["strikes"], p["K"]
    
    # 1. 處理局數顯示與浮點數轉換
    full_innings = total_outs // 3
    remaining_outs = total_outs % 3
    ip_display = f"{full_innings}.{remaining_outs}" # 轉化為常見的 5.1, 5.2 格式
    ip_float = full_innings + (remaining_outs / 3.0) # 精確計算用的浮點數
    
    # 2. 防禦率 ERA = ER * 9 / IP
    era = (er * 9.0 / ip_float) if ip_float > 0 else 0.0
    era_str = f"{era:.2f}"
    
    # 3. 好球率 = (好球 / 總投球數) * 100%
    strike_pct = (strikes / pitches * 100) if pitches > 0 else 0.0
    strike_str = f"{strike_pct:.1f}%"
    
    # 4. K/9 值 = K * 9 / IP
    k9 = (k * 9.0 / ip_float) if ip_float > 0 else 0.0
    k9_str = f"{k9:.2f}"
    
    return {"ip": ip_display, "era": era_str, "strike_pct": strike_str, "k9": k9_str}


# ==============================================================================
# 4. 展示層 (HTML View with CSS)
# ==============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>台啤盃完整數據庫</title>
    <style>
        body { font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 30px; background-color: #f4f4f9; }
        h1, h2 { text-align: center; color: #1a4a25; }
        .container { max-width: 1100px; margin: 0 auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: center; border-bottom: 1px solid #ddd; }
        th { background-color: #1e7e34; color: white; }
        .highlight { font-weight: bold; color: #1e7e34; }
        .btn { padding: 4px 8px; font-size: 12px; border: none; border-radius: 4px; cursor: pointer; margin: 2px; color: white; font-weight: bold;}
        .btn-green { background-color: #28a745; }
        .btn-red { background-color: #dc3545; }
        .btn-blue { background-color: #007bff; }
        .btn-orange { background-color: #ff9800; }
    </style>
</head>
<body>

    <h1>🍺 台啤盃自動化數據管理系統 🍺</h1>
    
    <div class="container">
        <h2>🏏 打者數據榜 (Batting Module)</h2>
        <table>
            <thead>
                <tr>
                    <th>球員</th>
                    <th>球隊</th>
                    <th>打席(PA)</th>
                    <th>打數(AB)</th>
                    <th>安打(H)</th>
                    <th>四壞(BB)</th>
                    <th>觸身(HBP)</th>
                    <th>犧牲(SAC)</th>
                    <th>打擊率(AVG)</th>
                    <th>上壘率(OBP)</th>
                    <th>紀錄員即時輸入面板</th>
                </tr>
            </thead>
            <tbody>
                {% for b in batters %}
                <tr>
                    <td><strong>{{ b.name }}</strong></td>
                    <td>{{ b.team }}</td>
                    <td>{{ b.calc.pa }}</td>
                    <td>{{ b.AB }}</td>
                    <td>{{ b.H }}</td>
                    <td>{{ b.BB }}</td>
                    <td>{{ b.HBP }}</td>
                    <td>{{ b.SAC }}</td>
                    <td class="highlight">{{ b.calc.avg }}</td>
                    <td class="highlight">{{ b.calc.obp }}</td>
                    <td>
                        <form action="/batter/hit/{{ b.id }}" method="POST" style="display:inline;"><button class="btn btn-green">H (安打)</button></form>
                        <form action="/batter/out/{{ b.id }}" method="POST" style="display:inline;"><button class="btn btn-red">OUT (出局)</button></form>
                        <form action="/batter/bb/{{ b.id }}" method="POST" style="display:inline;"><button class="btn btn-blue">BB (保送)</button></form>
                        <form action="/batter/hbp/{{ b.id }}" method="POST" style="display:inline;"><button class="btn btn-blue">HBP (觸身)</button></form>
                        <form action="/batter/sac/{{ b.id }}" method="POST" style="display:inline;"><button class="btn btn-orange">SAC (犧牲)</button></form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="container">
        <h2>⚾ 投手數據榜 (Pitching Module)</h2>
        <table>
            <thead>
                <tr>
                    <th>球員</th>
                    <th>球隊</th>
                    <th>局數(IP)</th>
                    <th>總球數</th>
                    <th>好球數</th>
                    <th>自責分(ER)</th>
                    <th>奪三振(K)</th>
                    <th>防禦率(ERA)</th>
                    <th>好球率</th>
                    <th>K/9 值</th>
                    <th>紀錄員即時輸入面板</th>
                </tr>
            </thead>
            <tbody>
                {% for p in pitchers %}
                <tr>
                    <td><strong>{{ p.name }}</strong></td>
                    <td>{{ p.team }}</td>
                    <td class="highlight">{{ p.calc.ip }}</td>
                    <td>{{ p.pitches }}</td>
                    <td>{{ p.strikes }}</td>
                    <td>{{ p.ER }}</td>
                    <td>{{ p.K }}</td>
                    <td class="highlight">{{ p.calc.era }}</td>
                    <td class="highlight">{{ p.calc.strike_pct }}</td>
                    <td>{{ p.calc.k9 }}</td>
                    <td>
                        <form action="/pitcher/strike/{{ p.id }}" method="POST" style="display:inline;"><button class="btn btn-green">好球 (Strike)</button></form>
                        <form action="/pitcher/ball/{{ p.id }}" method="POST" style="display:inline;"><button class="btn btn-blue">壞球 (Ball)</button></form>
                        <form action="/pitcher/out/{{ p.id }}" method="POST" style="display:inline;"><button class="btn btn-red">抓到出局 (Out)</button></form>
                        <form action="/pitcher/er/{{ p.id }}" method="POST" style="display:inline;"><button class="btn btn-orange">失自責分 (ER)</button></form>
                        <form action="/pitcher/k/{{ p.id }}" method="POST" style="display:inline;"><button class="btn btn-green">奪三振 (K)</button></form>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

</body>
</html>
"""

# ==============================================================================
# 1. 路由與邏輯層運作 (Routing & Controller)
# ==============================================================================

@app.route('/')
def home():
    # 打者即時連動計算
    for b in batters_db:
        b["calc"] = calculate_batting_stats(b)
    # 投手即時連動計算
    for p in pitchers_db:
        p["calc"] = calculate_pitching_stats(p)
        
    return render_template_string(HTML_TEMPLATE, batters=batters_db, pitchers=pitchers_db)

# ----------------- 打者事件 PBP 連動 -----------------
@app.route('/batter/hit/<int:id>', methods=['POST'])
def batter_hit(id):
    for b in batters_db:
        if b["id"] == id: b["H"]+=1; b["AB"]+=1; break # 構想：H+=1 且 AB+=1
    return redirect(url_for('home'))

@app.route('/batter/out/<int:id>', methods=['POST'])
def batter_out(id):
    for b in batters_db:
        if b["id"] == id: b["AB"]+=1; break # 構想：出局只加打數
    return redirect(url_for('home'))

@app.route('/batter/bb/<int:id>', methods=['POST'])
def batter_bb(id):
    for b in batters_db:
        if b["id"] == id: b["BB"]+=1; break # 過濾機制：只增加 BB，不增加打數 (AB)
    return redirect(url_for('home'))

@app.route('/batter/hbp/<int:id>', methods=['POST'])
def batter_hbp(id):
    for b in batters_db:
        if b["id"] == id: b["HBP"]+=1; break # 過濾機制：只增加 HBP，不增加打數 (AB)
    return redirect(url_for('home'))

@app.route('/batter/sac/<int:id>', methods=['POST'])
def batter_sac(id):
    for b in batters_db:
        if b["id"] == id: b["SAC"]+=1; break # 過濾機制：只增加 犧牲打，不增加打數 (AB)
    return redirect(url_for('home'))

# ----------------- 投手事件 PBP 連動 -----------------
@app.route('/pitcher/strike/<int:id>', methods=['POST'])
def pitcher_strike(id):
    for p in pitchers_db:
        if p["id"] == id: p["strikes"]+=1; p["pitches"]+=1; break # 好球數+1, 總球數+1
    return redirect(url_for('home'))

@app.route('/pitcher/ball/<int:id>', methods=['POST'])
def pitcher_ball(id):
    for p in pitchers_db:
        if p["id"] == id: p["pitches"]+=1; break # 壞球只加總球數
    return redirect(url_for('home'))

@app.route('/pitcher/out/<int:id>', methods=['POST'])
def pitcher_out(id):
    for p in pitchers_db:
        if p["id"] == id: p["total_outs"]+=1; break # 核心構想：紀錄總出局數
    return redirect(url_for('home'))

@app.route('/pitcher/er/<int:id>', methods=['POST'])
def pitcher_er(id):
    for p in pitchers_db:
        if p["id"] == id: p["ER"]+=1; break
    return redirect(url_for('home'))

@app.route('/pitcher/k/<int:id>', methods=['POST'])
def pitcher_k(id):
    for p in pitchers_db:
        if p["id"] == id: p["K"]+=1; p["strikes"]+=1; p["pitches"]+=1; break
    return redirect(url_for('home'))

import os

if __name__ == '__main__':
    # 讓網站能自動去讀取雲端平台指定的 Port，如果在本機測試就預設用 5000
    port = int(os.environ.get('PORT', 5000))
    # 關鍵：host='0.0.0.0' 代表大門打開，允許雲端平台把流量導進來
    app.run(host='0.0.0.0', port=port, debug=False)