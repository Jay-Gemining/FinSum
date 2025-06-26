import React, { useState, useEffect } from 'react';
import axios from 'axios'; // 使用 axios 进行 API 调用

import Header from './components/Header';
import ExecutiveSummary from './components/ExecutiveSummary';
import MarketSentiment from './components/MarketSentiment';
import KeyIndices from './components/KeyIndices';
import TopStories from './components/TopStories';
import Footer from './components/Footer';
import SkeletonLoader from './components/SkeletonLoader'; // 稍后将创建此组件

function App() {
  const [reportData, setReportData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // vite.config.js 代理会将此请求重定向到 http://localhost:8000/api/report
      const response = await axios.get('/api/report');
      setReportData(response.data);
    } catch (err) {
      console.error("获取报告时出错:", err);
      setError(err.response?.data?.detail || "报告生成失败。请稍后再试。");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []); // 空依赖数组表示此 effect 仅在挂载时运行一次

  if (isLoading) {
    return <SkeletonLoader />;
  }

  if (error) {
    return (
      <div className="container">
        <Header reportDate={new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', year: 'numeric' })} />
        <div className="error-message card">
          <h2>错误</h2>
          <p>{error}</p>
          <button onClick={fetchReport} style={{marginTop: '1rem'}}>重试</button>
        </div>
        <Footer />
      </div>
    );
  }

  if (!reportData) {
    // 理想情况下，如果未加载且没有错误，则不应发生这种情况，但作为后备
    return (
        <div className="container">
            <Header reportDate={new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', year: 'numeric' })} />
            <div className="loading-message card"><p>没有可用的报告数据。</p></div>
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
