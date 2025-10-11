'use client';

import React from 'react';
import { Event, sortEventsByDate, isEventToday, isEventThisWeek } from '@/types/events';
import EventCard from './EventCard';

interface EventListProps {
  events: Event[];
  loading?: boolean;
  error?: string;
}

const EventList: React.FC<EventListProps> = ({ events, loading, error }) => {
  if (loading) {
    return (
      <div className="content-block">
        <div className="content-block-header">
          Events
        </div>
        <div className="content-block-body">
          <div className="loading">
            Loading events
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="content-block">
        <div className="content-block-header">
          Events
        </div>
        <div className="content-block-body">
          <div className="error">
            Error loading events: {error}
          </div>
        </div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="content-block">
        <div className="content-block-header">
          Events
        </div>
        <div className="content-block-body">
          <div style={{ textAlign: 'center', color: '#666666', fontStyle: 'italic' }}>
            No events found matching your criteria.
          </div>
        </div>
      </div>
    );
  }

  // Sort events by date
  const sortedEvents = sortEventsByDate(events);
  
  // Group events by time period
  const todayEvents = sortedEvents.filter(isEventToday);
  const thisWeekEvents = sortedEvents.filter(event => 
    !isEventToday(event) && isEventThisWeek(event)
  );
  const futureEvents = sortedEvents.filter(event => 
    !isEventToday(event) && !isEventThisWeek(event)
  );

  const renderEventGroup = (title: string, events: Event[], icon: string) => {
    if (events.length === 0) return null;

    return (
      <div key={title} style={{ marginBottom: '25px' }}>
        <h3 style={{ 
          fontSize: '16px', 
          marginBottom: '10px',
          color: '#333333',
          borderBottom: '1px solid #cccccc',
          paddingBottom: '5px'
        }}>
          {icon} {title} ({events.length})
        </h3>
        <ul className="event-list">
          {events.map(event => (
            <li key={event.id}>
              <EventCard event={event} />
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="content-block">
      <div className="content-block-header">
        Events ({events.length} total)
      </div>
      <div className="content-block-body">
        {renderEventGroup("Today's Events", todayEvents, "📅")}
        {renderEventGroup("This Week", thisWeekEvents, "📆")}
        {renderEventGroup("Upcoming Events", futureEvents, "🔮")}
      </div>
    </div>
  );
};

export default EventList;
