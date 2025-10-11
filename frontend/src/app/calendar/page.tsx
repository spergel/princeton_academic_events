'use client';

import React from 'react';
import Header from '@/components/Header';
import Link from 'next/link';

export default function CalendarPage() {
  return (
    <div>
      <Header />
      
      <div className="container">
        <div className="content-block">
          <div className="content-block-header">
            Calendar View
          </div>
          <div className="content-block-body">
            <div style={{ textAlign: 'center', padding: '40px 20px' }}>
              <h2 style={{ marginBottom: '20px' }}>📅 Calendar View</h2>
              <p style={{ marginBottom: '20px', color: '#666666' }}>
                The calendar view is coming soon! This will display all events in a traditional calendar format.
              </p>
              <div style={{ marginBottom: '20px' }}>
                <Link href="/" className="button button-primary">
                  ← Back to List View
                </Link>
              </div>
              <div className="academic-note">
                <strong>Planned Features:</strong><br />
                • Monthly calendar grid view<br />
                • Event details on hover<br />
                • Department color coding<br />
                • Export to personal calendar<br />
                • Mobile-responsive design
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <footer className="footer">
        <div className="container">
          <p>
            Princeton Academic Events | 
            <a href="https://www.princeton.edu" target="_blank" rel="noopener noreferrer">
              Princeton University
            </a> | 
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>
      </footer>
    </div>
  );
}
