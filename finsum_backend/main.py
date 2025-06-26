from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import datetime

from core.cache import get_cached_report, set_cached_report
from core.report_generator import generate_report_data # 占位符

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 为简单起见，在 MVP 中允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/report")
async def get_report():
    """
    获取金融市场报告的端点。
    首先检查缓存，如果需要则生成新报告。
    """
    today_str = datetime.date.today().isoformat()
    cached_report = get_cached_report(today_str)

    if cached_report:
        print("从缓存提供服务")
        return cached_report

    print("正在生成新报告")
    try:
        # 在实际场景中，report_generator.generate_report_data() 将
        # 触发数据获取和 LLM 处理。
        # 目前，它可能是一个占位符。
        report_data = await generate_report_data() # 假设它是一个异步函数
        set_cached_report(today_str, report_data)
        return report_data
    except Exception as e:
        # 记录异常 e
        print(f"生成报告时出错：{e}")
        raise HTTPException(status_code=500, detail="未能生成报告。")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
