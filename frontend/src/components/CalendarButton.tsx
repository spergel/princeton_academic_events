'use client';

import React from 'react';
import Link from 'next/link';

interface CalendarButtonProps {
  eventCount?: number;
}

const CalendarButton: React.FC<CalendarButtonProps> = ({ eventCount }) => {
  return (
    <div style={{ textAlign: 'center', margin: '20px 0' }}>
      <Link href="/calendar" className="calendar-button">
        📅 View as Calendar
        {eventCount && (
          <span style={{ 
            marginLeft: '8px', 
            fontSize: '14px',
            opacity: 0.9 
          }}>
            ({eventCount} events)
          </span>
        )}
      </Link>
    </div>
  );
};

export default CalendarButton;
