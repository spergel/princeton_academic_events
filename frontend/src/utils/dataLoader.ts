// Static data loading utilities for the Princeton Academic Events site

import { Event, Department } from '@/types/events';

// Data interfaces for static files
interface EventsData {
  events: Event[];
  metadata: {
    total_events: number;
    total_departments: number;
    files_processed: number;
    successful_files: number;
    aggregated_at: string;
    deduplication_removed: number;
  };
}

interface DepartmentsData {
  departments: Department[];
  departments_by_category: Record<string, Department[]>;
  meta_categories: Record<string, string>;
  total_departments: number;
  generated_at: string;
}

interface MetaData {
  site_info: {
    name: string;
    description: string;
    version: string;
  };
  stats: {
    total_events: number;
    total_departments: number;
    last_updated: string;
  };
  build_info: {
    build_date: string;
    data_source: string;
    update_frequency: string;
  };
}

// Cache for loaded data
let eventsCache: EventsData | null = null;
let departmentsCache: DepartmentsData | null = null;
let metaCache: MetaData | null = null;

export async function loadEventsData(): Promise<EventsData> {
  if (eventsCache) {
    return eventsCache;
  }

  try {
    const response = await fetch('/data/events.json');
    if (!response.ok) {
      throw new Error(`Failed to load events: ${response.status}`);
    }
    
    const data = await response.json();
    eventsCache = data;
    return data;
  } catch (error) {
    console.error('Error loading events data:', error);
    // Return empty data structure on error
    return {
      events: [],
      metadata: {
        total_events: 0,
        total_departments: 0,
        files_processed: 0,
        successful_files: 0,
        aggregated_at: new Date().toISOString(),
        deduplication_removed: 0
      }
    };
  }
}

export async function loadDepartmentsData(): Promise<DepartmentsData> {
  if (departmentsCache) {
    return departmentsCache;
  }

  try {
    const response = await fetch('/data/departments.json');
    if (!response.ok) {
      throw new Error(`Failed to load departments: ${response.status}`);
    }
    
    const data = await response.json();
    departmentsCache = data;
    return data;
  } catch (error) {
    console.error('Error loading departments data:', error);
    // Return empty data structure on error
    return {
      departments: [],
      departments_by_category: {},
      meta_categories: {},
      total_departments: 0,
      generated_at: new Date().toISOString()
    };
  }
}

export async function loadMetaData(): Promise<MetaData> {
  if (metaCache) {
    return metaCache;
  }

  try {
    const response = await fetch('/data/meta.json');
    if (!response.ok) {
      throw new Error(`Failed to load meta data: ${response.status}`);
    }
    
    const data = await response.json();
    metaCache = data;
    return data;
  } catch (error) {
    console.error('Error loading meta data:', error);
    // Return default meta data on error
    return {
      site_info: {
        name: 'Princeton Academic Events',
        description: 'Academic events across Princeton University',
        version: '1.0.0'
      },
      stats: {
        total_events: 0,
        total_departments: 0,
        last_updated: new Date().toISOString()
      },
      build_info: {
        build_date: new Date().toISOString(),
        data_source: 'Princeton University Department Websites',
        update_frequency: 'Weekly'
      }
    };
  }
}

// Combined data loading function
export async function loadAllData(): Promise<{
  events: Event[];
  departments: Department[];
  meta: MetaData;
}> {
  const [eventsData, departmentsData, metaData] = await Promise.all([
    loadEventsData(),
    loadDepartmentsData(),
    loadMetaData()
  ]);

  return {
    events: eventsData.events,
    departments: departmentsData.departments,
    meta: metaData
  };
}

// Clear cache (useful for development)
export function clearDataCache(): void {
  eventsCache = null;
  departmentsCache = null;
  metaCache = null;
}

// Check if data is stale (older than 7 days)
export function isDataStale(lastUpdated: string): boolean {
  const lastUpdate = new Date(lastUpdated);
  const now = new Date();
  const daysDiff = (now.getTime() - lastUpdate.getTime()) / (1000 * 60 * 60 * 24);
  return daysDiff > 7;
}
