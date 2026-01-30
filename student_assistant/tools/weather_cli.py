import argparse
import json
import random
from datetime import datetime, timedelta

def query_weather(date_str):
    # 解析日期
    target_date = date_str
    if date_str == 'today':
        target_date = datetime.now().strftime("%Y-%m-%d")
    elif date_str == 'tomorrow':
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Mock 数据生成逻辑
    weathers = ["晴", "多云", "阴", "小雨", "大雨", "雷阵雨"]
    weather = random.choice(weathers)
    
    # 根据天气生成合理的温度
    base_temp = 20 # 假设是春秋季
    if "雨" in weather:
        temp_high = base_temp - random.randint(2, 5)
        temp_low = temp_high - random.randint(5, 8)
        rain_prob = random.randint(60, 95)
    elif "晴" in weather:
        temp_high = base_temp + random.randint(3, 8)
        temp_low = temp_high - random.randint(10, 15)
        rain_prob = random.randint(0, 10)
    else:
        temp_high = base_temp
        temp_low = base_temp - random.randint(5, 10)
        rain_prob = random.randint(10, 40)
        
    data = {
        "date": target_date,
        "weather": weather,
        "temp_high": temp_high,
        "temp_low": temp_low,
        "rain_prob": rain_prob, # 降水概率 %
        "suggestion": ""
    }
    
    # 生成建议
    if rain_prob > 50:
        data["suggestion"] = "记得带伞哦！"
    elif temp_high > 30:
        data["suggestion"] = "天气较热，注意防暑。"
    elif temp_low < 10:
        data["suggestion"] = "天气转凉，多穿点衣服。"
    else:
        data["suggestion"] = "天气不错，适合出门。"
        
    return {"success": True, "data": data}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="天气查询工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    query_parser = subparsers.add_parser("query", help="查询天气")
    query_parser.add_argument("--date", required=True, help="日期 today/tomorrow/YYYY-MM-DD")
    
    args = parser.parse_args()
    
    if args.command == "query":
        print(json.dumps(query_weather(args.date), ensure_ascii=False))
    else:
        parser.print_help()
