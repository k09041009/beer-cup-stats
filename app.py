from flask import Flask, render_template_string, redirect, url_for, request
import os

app = Flask(__name__)

# ==============================================================================
# 1. 擴充數據庫結構 (Data Schema) - 六大球隊與小字輩球員登場
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

# 今日賽事對戰組合資訊（更新為今日重頭戲）
today_match = {
    "team_A": "台灣啤酒",
    "team_B": "台北市大",
    "time": "18:30",
    "stadium": "天母棒球場",
    "weather": "晴朗 29°C"
}

# ==============================================================================
# 2. 運算層 (Core Logic)
# ==============================================================================
def process_data(search_query=None):
    processed = []
    for b in batters_db:
        pa = b["AB"] + b["BB"] + b["HBP"] + b["SAC"]
        avg = (b["H"] / b["AB"]) if b["AB"] > 0 else 0.0
        obp = (b["H"] + b["BB"] + b["HBP"]) / pa if pa > 0 else 0.0
        
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
            "obp": f"{obp:.3f}".lstrip('0') if obp < 1.0 else f"{obp:.3f}",
            "g3_avg": f"{g3_avg:.3f}".lstrip('0') if g3_avg < 1.0 else f"{g3_avg:.3f}",
            "g5_avg": f"{g5_avg:.3f}".lstrip('0') if g5_avg < 1.0 else f"{g5_avg:.3f}",
            "avg_raw": avg, "g3_raw": g3_avg, "g5_raw": g5_avg
        })
        processed.append(p_dict)
    return processed

# ==============================================================================
# 3. 展示層 (HTML 介面)
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
        .tab:hover