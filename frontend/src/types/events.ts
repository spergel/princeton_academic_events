// TypeScript interfaces for Princeton Academic Events

export interface Event {
  id: string;
  title: string;
  description: string;
  start_date: string;
  end_date?: string | null;
  time: string;
  location: string;
  event_type: string;
  department: string;
  meta_category: string;
  source_url: string;
  source_name: string;
  speaker?: string;
  audience?: string;
  topics: string[];
  departments: string[];
  tags: string[];
  series?: string;
  speaker_affiliation?: string;
  speaker_url?: string;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface EventMetadata {
  department: string;
  total_events: number;
  scraped_at: string;
  source_url: string;
  source: string;
  note: string;
}

export interface EventResponse {
  metadata: EventMetadata;
  events: Event[];
}

export interface Department {
  name: string;
  meta_category: string;
  event_count: number;
  is_selected: boolean;
}

export interface MetaCategory {
  name: string;
  display_name: string;
  departments: Department[];
  color: string;
}

export interface FilterState {
  selected_departments: string[];
  selected_meta_categories: string[];
  search_query: string;
  date_range: {
    start: string;
    end: string;
  };
  event_types: string[];
}

export interface CalendarEvent {
  id: string;
  title: string;
  start: Date;
  end?: Date;
  location: string;
  department: string;
  event_type: string;
  color: string;
}

// Department configurations matching the backend
export const META_CATEGORIES: MetaCategory[] = [
  {
    name: 'arts_humanities',
    display_name: 'Arts & Humanities',
    departments: [],
    color: '#4a90a4'
  },
  {
    name: 'social_sciences',
    display_name: 'Social Sciences',
    departments: [],
    color: '#7cb342'
  },
  {
    name: 'sciences_engineering',
    display_name: 'Sciences & Engineering',
    departments: [],
    color: '#a44a90'
  },
  {
    name: 'area_studies',
    display_name: 'Area Studies',
    departments: [],
    color: '#a47c4a'
  },
  {
    name: 'interdisciplinary',
    display_name: 'Interdisciplinary',
    departments: [],
    color: '#4a4aa4'
  }
];

// Event type configurations
export const EVENT_TYPES = [
  'Seminar',
  'Colloquium',
  'Lecture',
  'Talk',
  'Workshop',
  'Conference',
  'Panel',
  'Discussion',
  'Symposium',
  'Meeting',
  'Presentation',
  'Kruzhok',
  'Artist Talk',
  'Exhibition',
  'Film Screening',
  'Event'
];

// Utility functions
export function getEventTypeColor(eventType: string): string {
  const typeColors: Record<string, string> = {
    'Seminar': '#ff8c00',
    'Colloquium': '#4a90a4',
    'Lecture': '#7cb342',
    'Talk': '#a44a90',
    'Workshop': '#a47c4a',
    'Conference': '#4a4aa4',
    'Panel': '#ff6b6b',
    'Discussion': '#4ecdc4',
    'Symposium': '#45b7d1',
    'Meeting': '#96ceb4',
    'Presentation': '#feca57',
    'Kruzhok': '#ff9ff3',
    'Artist Talk': '#54a0ff',
    'Exhibition': '#5f27cd',
    'Film Screening': '#00d2d3',
    'Event': '#ff8c00'
  };
  
  return typeColors[eventType] || '#ff8c00';
}

export function getMetaCategoryColor(metaCategory: string): string {
  const categoryColors: Record<string, string> = {
    'arts_humanities': '#4a90a4',
    'social_sciences': '#7cb342',
    'sciences_engineering': '#a44a90',
    'area_studies': '#a47c4a',
    'interdisciplinary': '#4a4aa4'
  };
  
  return categoryColors[metaCategory] || '#ff8c00';
}

export function formatEventDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch {
    return dateString;
  }
}

export function formatEventTime(timeString: string): string {
  if (!timeString) return '';
  
  // Handle time ranges like "2:00 PM – 4:00 PM"
  if (timeString.includes('–')) {
    return timeString;
  }
  
  // Handle single times
  return timeString;
}

export function isEventToday(event: Event): boolean {
  try {
    const eventDate = new Date(event.start_date);
    const today = new Date();
    return eventDate.toDateString() === today.toDateString();
  } catch {
    return false;
  }
}

export function isEventThisWeek(event: Event): boolean {
  try {
    const eventDate = new Date(event.start_date);
    const today = new Date();
    const weekFromNow = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    return eventDate >= today && eventDate <= weekFromNow;
  } catch {
    return false;
  }
}

export function sortEventsByDate(events: Event[]): Event[] {
  return [...events].sort((a, b) => {
    const dateA = new Date(a.start_date);
    const dateB = new Date(b.start_date);
    return dateA.getTime() - dateB.getTime();
  });
}

export function filterEventsByDepartment(events: Event[], departments: string[]): Event[] {
  if (departments.length === 0) return events;
  return events.filter(event => departments.includes(event.department));
}

export function filterEventsBySearch(events: Event[], query: string): Event[] {
  if (!query.trim()) return events;
  
  const searchQuery = query.toLowerCase();
  return events.filter(event => 
    event.title.toLowerCase().includes(searchQuery) ||
    event.description.toLowerCase().includes(searchQuery) ||
    event.speaker?.toLowerCase().includes(searchQuery) ||
    event.location.toLowerCase().includes(searchQuery) ||
    event.department.toLowerCase().includes(searchQuery) ||
    event.tags.some(tag => tag.toLowerCase().includes(searchQuery))
  );
}
