import React from 'react';
import './KeyIndices.css';

const IndexCard = ({ name, price, change, changePercent }) => {
  // Determine class for text color based on change value
  let changeClass = 'text-neutral'; // Default to neutral
  if (change && typeof change === 'string' && change !== "N/A") {
    if (change.startsWith('+')) {
      changeClass = 'text-positive';
    } else if (change.startsWith('-')) {
      changeClass = 'text-negative';
    }
    // If it's "0.00" or similar without a sign, it remains neutral or could be styled distinctly if needed
  }

  return (
    <div className="index-card"> {/* This is the sub-card */}
      <h3>{name}</h3>
      <p className="index-price">{price || 'N/A'}</p>
      <p className={`index-change ${changeClass}`}>
        {change || 'N/A'} ({changePercent || 'N/A'})
      </p>
    </div>
  );
};

const KeyIndices = ({ indices }) => {
  if (!indices || Object.keys(indices).length === 0) {
    // Optionally, render a placeholder or message if indices are expected but missing
    return (
        <section className="key-indices card">
            <h2>关键指数</h2>
            <p>Market data is currently unavailable.</p>
        </section>
    );
  }

  return (
    <section className="key-indices card"> {/* This is the main card */}
      <h2>关键指数</h2>
      <div className="indices-container"> {/* Flex/Grid container for sub-cards */}
        {Object.entries(indices).map(([name, data]) => (
          <IndexCard
            key={name}
            name={name}
            price={data.price}
            change={data.change}
            changePercent={data.change_percent}
          />
        ))}
      </div>
    </section>
  );
};

export default KeyIndices;
