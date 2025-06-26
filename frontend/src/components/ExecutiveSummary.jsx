import React from 'react';
import './ExecutiveSummary.css';

const ExecutiveSummary = ({ summary }) => {
  if (!summary) return null;

  return (
    <section className="executive-summary card">
      <h2>今日摘要</h2>
      <p className="summary-text">{summary}</p>
    </section>
  );
};

export default ExecutiveSummary;
