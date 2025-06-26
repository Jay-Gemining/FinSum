import React from 'react';
import './KeyIndices.css';

const IndexCard = ({ name, price, change, changePercent }) => {
  // 根据变化值确定文本颜色的类名
  let changeClass = 'text-neutral'; // 默认为中性
  if (change && typeof change === 'string' && change !== "N/A") {
    if (change.startsWith('+')) {
      changeClass = 'text-positive';
    } else if (change.startsWith('-')) {
      changeClass = 'text-negative';
    }
    // 如果是 "0.00" 或类似没有符号的值，则保持中性，或者如果需要可以设置独特的样式
  }

  return (
    <div className="index-card"> {/* 这是子卡片 */}
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
    // 可选：如果预期有指数但缺失，则渲染占位符或消息
    return (
        <section className="key-indices card">
            <h2>关键指数</h2>
            <p>市场数据当前不可用。</p>
        </section>
    );
  }

  return (
    <section className="key-indices card"> {/* 这是主卡片 */}
      <h2>关键指数</h2>
      <div className="indices-container"> {/* 子卡片的 Flex/Grid 容器 */}
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
