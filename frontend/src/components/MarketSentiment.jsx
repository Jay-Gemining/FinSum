import React from 'react';
import './MarketSentiment.css';

const MarketSentiment = ({ sentiment, reason }) => {
  if (!sentiment) return null;

  const sentimentClass = `sentiment-badge sentiment-${sentiment.toLowerCase()}`;

  return (
    <section className="market-sentiment card">
      <h2>市场情绪</h2>
      <div style={{ marginBottom: 'var(--spacing-sm)'}}>
        <span className={sentimentClass}>{sentiment}</span>
      </div>
      <p className="sentiment-reason">{reason}</p>
    </section>
  );
};

export default MarketSentiment;
