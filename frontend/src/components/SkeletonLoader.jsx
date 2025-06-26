import React from 'react';
import './SkeletonLoader.css'; // 稍后我们将创建此 CSS 文件

const SkeletonLoader = () => {
  return (
    <div className="skeleton-container">
      {/* 页眉骨架 */}
      <div className="skeleton-header card">
        <div className="skeleton-line " style={{ width: '30%', height: '24px' }}></div>
        <div className="skeleton-line " style={{ width: '20%', height: '20px', marginLeft: 'auto' }}></div>
      </div>

      {/* 执行摘要骨架 */}
      <div className="skeleton-card card">
        <div className="skeleton-line " style={{ width: '40%', height: '20px', marginBottom: 'var(--spacing-sm)' }}></div>
        <div className="skeleton-line " style={{ width: '90%', height: '24px' }}></div>
        <div className="skeleton-line " style={{ width: '80%', height: '24px' }}></div>
      </div>

      {/* 市场情绪骨架 */}
      <div className="skeleton-card card">
        <div className="skeleton-line " style={{ width: '30%', height: '20px', marginBottom: 'var(--spacing-sm)' }}></div>
        <div className="skeleton-line " style={{ width: '20%', height: '28px', borderRadius: 'var(--border-radius-sm)', marginBottom: 'var(--spacing-sm)' }}></div>
        <div className="skeleton-line " style={{ width: '100%' }}></div>
        <div className="skeleton-line " style={{ width: '100%' }}></div>
        <div className="skeleton-line " style={{ width: '60%' }}></div>
      </div>

      {/* 关键指数骨架 */}
      <div className="skeleton-card card">
        <div className="skeleton-line " style={{ width: '30%', height: '20px', marginBottom: 'var(--spacing-lg)' }}></div>
        <div className="skeleton-indices-grid">
          <div className="skeleton-index-item">
            <div className="skeleton-line " style={{ width: '50%', height: '18px' }}></div>
            <div className="skeleton-line " style={{ width: '70%', height: '30px', margin: 'var(--spacing-sm) 0' }}></div>
            <div className="skeleton-line " style={{ width: '40%', height: '16px' }}></div>
          </div>
          <div className="skeleton-index-item">
            <div className="skeleton-line " style={{ width: '50%', height: '18px' }}></div>
            <div className="skeleton-line " style={{ width: '70%', height: '30px', margin: 'var(--spacing-sm) 0' }}></div>
            <div className="skeleton-line " style={{ width: '40%', height: '16px' }}></div>
          </div>
        </div>
      </div>

      {/* 头条新闻骨架 */}
      <div className="skeleton-card card">
        <div className="skeleton-line " style={{ width: '35%', height: '20px', marginBottom: 'var(--spacing-lg)' }}></div>
        {[1, 2, 3].map(i => (
          <div key={i} className="skeleton-story-item">
            <div className="skeleton-line " style={{ width: '80%', height: '18px', fontWeight: 'bold' }}></div>
            <div className="skeleton-line " style={{ width: '100%', marginTop: 'var(--spacing-xs)' }}></div>
            <div className="skeleton-line " style={{ width: '100%', marginTop: 'var(--spacing-xs)' }}></div>
            <div className="skeleton-line " style={{ width: '30%', height: '16px', marginTop: 'var(--spacing-xs)' }}></div>
            {i < 3 && <div className="skeleton-separator"></div>}
          </div>
        ))}
      </div>

      {/* 页脚骨架 */}
      <div className="skeleton-footer">
        <div className="skeleton-line " style={{ width: '20%', height: '16px', margin: '0 auto' }}></div>
      </div>
    </div>
  );
};

export default SkeletonLoader;
