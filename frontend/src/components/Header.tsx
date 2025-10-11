'use client';

import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="container">
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div className="princeton-logo"></div>
          <h1>Princeton Academic Events</h1>
        </div>
        <p style={{ margin: '5px 0 0 0', fontSize: '12px', color: '#ffffff' }}>
          Discover academic events across Princeton University
        </p>
      </div>
    </header>
  );
};

export default Header;
