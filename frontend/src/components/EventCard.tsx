'use client';

import React from 'react';
import { Event, getEventTypeColor, formatEventDate, formatEventTime } from '@/types/events';

interface EventCardProps {
  event: Event;
  showDepartment?: boolean;
}

const EventCard: React.FC<EventCardProps> = ({ event, showDepartment = true }) => {
  const eventTypeColor = getEventTypeColor(event.event_type);

  return (
    <div className="event-item">
      <div className="event-title">
        <a href={event.source_url} target="_blank" rel="noopener noreferrer">
          {event.title}
        </a>
        <span 
          className="event-type-badge"
          style={{ 
            backgroundColor: eventTypeColor + '20',
            borderColor: eventTypeColor,
            color: eventTypeColor
          }}
        >
          {event.event_type}
        </span>
      </div>
      
      <div className="event-meta">
        <strong>📅 {formatEventDate(event.start_date)}</strong>
        {event.time && (
          <span style={{ marginLeft: '15px' }}>
            <strong>🕐 {formatEventTime(event.time)}</strong>
          </span>
        )}
      </div>
      
      <div className="event-meta">
        <strong>📍 {event.location}</strong>
      </div>
      
      {event.speaker && (
        <div className="event-meta">
          <strong>👤 {event.speaker}</strong>
          {event.speaker_affiliation && (
            <span style={{ marginLeft: '10px', fontStyle: 'italic' }}>
              ({event.speaker_affiliation})
            </span>
          )}
        </div>
      )}
      
      {showDepartment && (
        <div className="event-meta">
          <span 
            className="department-tag"
            style={{ 
              backgroundColor: event.meta_category === 'arts_humanities' ? '#e8f4f8' :
                              event.meta_category === 'social_sciences' ? '#f0f8e8' :
                              event.meta_category === 'sciences_engineering' ? '#f8e8f0' :
                              event.meta_category === 'area_studies' ? '#f8f0e8' :
                              event.meta_category === 'interdisciplinary' ? '#e8e8f8' : '#f5f5f5',
              borderColor: event.meta_category === 'arts_humanities' ? '#4a90a4' :
                          event.meta_category === 'social_sciences' ? '#7cb342' :
                          event.meta_category === 'sciences_engineering' ? '#a44a90' :
                          event.meta_category === 'area_studies' ? '#a47c4a' :
                          event.meta_category === 'interdisciplinary' ? '#4a4aa4' : '#cccccc'
            }}
          >
            {event.department}
          </span>
        </div>
      )}
      
      {event.description && (
        <div style={{ 
          marginTop: '8px', 
          fontSize: '13px', 
          color: '#555555',
          lineHeight: '1.4'
        }}>
          {event.description.length > 200 
            ? `${event.description.substring(0, 200)}...` 
            : event.description
          }
        </div>
      )}
      
      {event.tags && event.tags.length > 0 && (
        <div style={{ marginTop: '8px' }}>
          {event.tags.slice(0, 5).map((tag, index) => (
            <span 
              key={index}
              style={{
                display: 'inline-block',
                padding: '1px 4px',
                backgroundColor: '#f0f0f0',
                border: '1px solid #cccccc',
                fontSize: '10px',
                color: '#666666',
                marginRight: '3px',
                marginBottom: '2px'
              }}
            >
              {tag}
            </span>
          ))}
          {event.tags.length > 5 && (
            <span style={{ fontSize: '10px', color: '#999999' }}>
              +{event.tags.length - 5} more
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default EventCard;
