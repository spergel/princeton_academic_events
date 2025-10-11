'use client';

import React from 'react';

interface SearchBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  placeholder?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  searchQuery, 
  onSearchChange, 
  placeholder = "Search events..." 
}) => {
  return (
    <div className="content-block">
      <div className="content-block-header">
        Search Events
      </div>
      <div className="content-block-body">
        <input
          type="text"
          className="search-bar"
          placeholder={placeholder}
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
        />
        {searchQuery && (
          <div style={{ 
            fontSize: '12px', 
            color: '#666666', 
            marginTop: '5px' 
          }}>
            Searching for: &quot;{searchQuery}&quot;
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchBar;
