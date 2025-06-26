from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import datetime

from core.cache import get_cached_report, set_cached_report
from core.report_generator import generate_report_data # Placeholder

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for simplicity in MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/report")
async def get_report():
    """
    Endpoint to get the financial market report.
    Checks cache first, then generates a new report if needed.
    """
    today_str = datetime.date.today().isoformat()
    cached_report = get_cached_report(today_str)

    if cached_report:
        print("Serving from cache")
        return cached_report

    print("Generating new report")
    try:
        # In a real scenario, report_generator.generate_report_data() would
        # trigger data fetching and LLM processing.
        # For now, it might be a placeholder.
        report_data = await generate_report_data() # Assuming it's an async function
        set_cached_report(today_str, report_data)
        return report_data
    except Exception as e:
        # Log the exception e
        print(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
