import React from 'react';
import './Header.css';

const Header = ({ reportDate }) => {
  return (
    <header className="app-header">
      <div className="logo">FinSum</div>
      <div className="report-date">{reportDate}</div>
    </header>
  );
};

export default Header;
