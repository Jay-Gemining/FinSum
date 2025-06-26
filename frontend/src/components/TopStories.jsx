import React from 'react';
import './TopStories.css';

const StoryItem = ({ title, summary, url, source }) => {
  return (
    <div className="story-item">
      <h3 className="story-title">{title}</h3>
      <p className="story-summary">{summary}</p>
      {url && url !== "#" && (
        <p className="story-source">
          来源: <a href={url} target="_blank" rel="noopener noreferrer">{source || 'Read more'}</a>
        </p>
      )}
    </div>
  );
};

const TopStories = ({ stories }) => {
  if (!stories || stories.length === 0) return null;

  return (
    <section className="top-stories card">
      <h2>今日核心新闻</h2>
      <div className="stories-list">
        {stories.map((story, index) => (
          <React.Fragment key={index}>
            <StoryItem
              title={story.title}
              summary={story.summary}
              url={story.url}
              source={story.source}
            />
            {index < stories.length - 1 && <hr className="story-separator" />}
          </React.Fragment>
        ))}
      </div>
    </section>
  );
};

export default TopStories;
