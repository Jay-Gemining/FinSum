import React, { useState, useEffect } from 'react';
import axios from 'axios'; // Using axios for API calls

import Header from './components/Header';
import ExecutiveSummary from './components/ExecutiveSummary';
import MarketSentiment from './components/MarketSentiment';
import KeyIndices from './components/KeyIndices';
import TopStories from './components/TopStories';
import Footer from './components/Footer';
import SkeletonLoader from './components/SkeletonLoader'; // Will create this next

function App() {
  const [reportData, setReportData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // The vite.config.js proxy will redirect this to http://localhost:8000/api/report
      const response = await axios.get('/api/report');
      setReportData(response.data);
    } catch (err) {
      console.error("Error fetching report:", err);
      setError(err.response?.data?.detail || "Report generation failed. Please try again later.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []); // Empty dependency array means this runs once on mount

  if (isLoading) {
    return <SkeletonLoader />;
  }

  if (error) {
    return (
      <div className="container">
        <Header reportDate={new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })} />
        <div className="error-message card">
          <h2>Error</h2>
          <p>{error}</p>
          <button onClick={fetchReport} style={{marginTop: '1rem'}}>Retry</button>
        </div>
        <Footer />
      </div>
    );
  }

  if (!reportData) {
    // Should ideally not happen if not loading and no error, but as a fallback
    return (
        <div className="container">
            <Header reportDate={new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })} />
            <div className="loading-message card"><p>No report data available.</p></div>
            <Footer />
        </div>
    );
  }

  return (
    <div className="container">
      <Header reportDate={reportData.report_date} />
      <main>
        <ExecutiveSummary summary={reportData.executive_summary} />
        <MarketSentiment sentiment={reportData.market_sentiment?.sentiment} reason={reportData.market_sentiment?.reason} />
        <KeyIndices indices={reportData.key_indices} />
        <TopStories stories={reportData.top_stories} />
      </main>
      <Footer />
    </div>
  );
}

export default App;
