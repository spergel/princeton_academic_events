'use client';

import React, { useState, useEffect } from 'react';
import Header from '@/components/Header';
import EventList from '@/components/EventList';
import DepartmentFilter from '@/components/DepartmentFilter';
import SearchBar from '@/components/SearchBar';
import CalendarButton from '@/components/CalendarButton';
import { 
  Event, 
  Department, 
  filterEventsByDepartment, 
  filterEventsBySearch 
} from '@/types/events';
import { loadAllData, isDataStale } from '@/utils/dataLoader';

// Mock data for development - replace with actual API calls
const mockEvents: Event[] = [
  {
    id: '1',
    title: 'Machine Learning in Healthcare: Opportunities and Challenges',
    description: 'A comprehensive overview of how machine learning is transforming healthcare delivery, from diagnosis to treatment optimization.',
    start_date: '2025-09-15',
    time: '2:00 PM – 3:30 PM',
    location: 'Sherrerd Hall 101',
    event_type: 'Seminar',
    department: 'Computer Science',
    meta_category: 'sciences_engineering',
    source_url: '#',
    source_name: 'Computer Science Events',
    speaker: 'Dr. Sarah Chen',
    speaker_affiliation: 'Stanford University',
    topics: ['machine learning', 'healthcare', 'AI'],
    departments: ['Computer Science'],
    tags: ['AI', 'healthcare', 'research'],
    created_at: '2025-09-04T10:00:00Z',
    updated_at: '2025-09-04T10:00:00Z'
  },
  {
    id: '2',
    title: 'The Future of Democracy in the Digital Age',
    description: 'Exploring how digital technologies are reshaping democratic institutions and civic engagement.',
    start_date: '2025-09-16',
    time: '4:30 PM – 6:00 PM',
    location: 'Robertson Hall 002',
    event_type: 'Lecture',
    department: 'Politics',
    meta_category: 'social_sciences',
    source_url: '#',
    source_name: 'Politics Events',
    speaker: 'Prof. Michael Rodriguez',
    speaker_affiliation: 'Princeton University',
    topics: ['democracy', 'digital technology', 'politics'],
    departments: ['Politics'],
    tags: ['democracy', 'technology', 'politics'],
    created_at: '2025-09-04T10:00:00Z',
    updated_at: '2025-09-04T10:00:00Z'
  },
  {
    id: '3',
    title: 'Shakespeare and Modern Performance',
    description: 'A discussion of contemporary approaches to staging Shakespeare in the 21st century.',
    start_date: '2025-09-17',
    time: '7:00 PM – 8:30 PM',
    location: 'McCarter Theatre',
    event_type: 'Talk',
    department: 'English',
    meta_category: 'arts_humanities',
    source_url: '#',
    source_name: 'English Events',
    speaker: 'Dr. Emma Thompson',
    speaker_affiliation: 'Royal Shakespeare Company',
    topics: ['Shakespeare', 'theater', 'performance'],
    departments: ['English'],
    tags: ['Shakespeare', 'theater', 'literature'],
    created_at: '2025-09-04T10:00:00Z',
    updated_at: '2025-09-04T10:00:00Z'
  }
];

const mockDepartments: Department[] = [
  { name: 'Computer Science', meta_category: 'sciences_engineering', event_count: 15, is_selected: false },
  { name: 'Politics', meta_category: 'social_sciences', event_count: 8, is_selected: false },
  { name: 'English', meta_category: 'arts_humanities', event_count: 12, is_selected: false },
  { name: 'History', meta_category: 'arts_humanities', event_count: 6, is_selected: false },
  { name: 'Sociology', meta_category: 'social_sciences', event_count: 9, is_selected: false },
  { name: 'Physics', meta_category: 'sciences_engineering', event_count: 11, is_selected: false },
  { name: 'African Studies', meta_category: 'area_studies', event_count: 5, is_selected: false },
  { name: 'University Center for Human Values', meta_category: 'interdisciplinary', event_count: 7, is_selected: false }
];

export default function HomePage() {
  const [events, setEvents] = useState<Event[]>(mockEvents);
  const [departments, setDepartments] = useState<Department[]>(mockDepartments);
  const [selectedDepartments, setSelectedDepartments] = useState<string[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // Filter events based on selected departments and search query
  const filteredEvents = React.useMemo(() => {
    let filtered = events;
    
    if (selectedDepartments.length > 0) {
      filtered = filterEventsByDepartment(filtered, selectedDepartments);
    }
    
    if (searchQuery.trim()) {
      filtered = filterEventsBySearch(filtered, searchQuery);
    }
    
    return filtered;
  }, [events, selectedDepartments, searchQuery]);

  // Load events from static data files
  useEffect(() => {
    const loadEvents = async () => {
      setLoading(true);
      try {
        const data = await loadAllData();
        setEvents(data.events);
        setDepartments(data.departments);
        
        // Check if data is stale
        if (isDataStale(data.meta.stats.last_updated)) {
          console.warn('Event data is older than 7 days - consider updating');
        }
        
        setError('');
      } catch (err) {
        setError('Failed to load events');
        console.error('Error loading events:', err);
        
        // Fallback to mock data in development
        if (process.env.NODE_ENV === 'development') {
          console.log('Using mock data as fallback');
          setEvents(mockEvents);
          setDepartments(mockDepartments);
        }
      } finally {
        setLoading(false);
      }
    };

    loadEvents();
  }, []);

  return (
    <div>
      <Header />
      
      <div className="container">
        <div className="two-column">
          {/* Main Content */}
          <div className="main-content">
            <SearchBar 
              searchQuery={searchQuery}
              onSearchChange={setSearchQuery}
            />
            
            <EventList 
              events={filteredEvents}
              loading={loading}
              error={error}
            />
            
            <CalendarButton eventCount={filteredEvents.length} />
          </div>
          
          {/* Sidebar */}
          <div className="sidebar">
            <DepartmentFilter
              departments={departments}
              selectedDepartments={selectedDepartments}
              onDepartmentChange={setSelectedDepartments}
            />
            
            <div className="content-block">
              <div className="content-block-header">
                View Options
              </div>
              <div className="content-block-body">
                <div style={{ marginBottom: '10px' }}>
                  <a href="/calendar" className="button" style={{ width: '100%', textAlign: 'center' }}>
                    📅 Calendar View
                  </a>
                </div>
                <div style={{ marginBottom: '10px' }}>
                  <button className="button" style={{ width: '100%', textAlign: 'center' }}>
                    📋 List View
                  </button>
                </div>
                <div>
                  <button 
                    className="button" 
                    style={{ width: '100%', textAlign: 'center' }}
                    onClick={() => setSearchQuery('')}
                  >
                    🔍 Clear Search
                  </button>
                </div>
              </div>
            </div>
            
            <div className="academic-note">
              <strong>About Princeton Academic Events</strong><br />
              This site aggregates academic events from departments across Princeton University. 
              Events are updated regularly and include seminars, lectures, workshops, and conferences.
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