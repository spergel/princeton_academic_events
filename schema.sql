-- Princeton Academic Events Database Schema v2.0

-- Events table (updated to match our scraper data structure)
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE, -- Our generated unique ID
    title TEXT NOT NULL,
    description TEXT,
    date DATE, -- Date field (matches worker code)
    time TEXT,
    location TEXT,
    department TEXT NOT NULL, -- Direct department name
    url TEXT, -- Event URL
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_events_department ON events(department);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
CREATE INDEX IF NOT EXISTS idx_events_title ON events(title);

-- Meta-categories mapping (stored as a view for easy querying)
CREATE VIEW IF NOT EXISTS department_categories AS
SELECT 
    department,
    CASE 
        WHEN department IN ('Philosophy', 'History', 'English', 'Classics', 'Religion', 'Comparative Literature', 'Art and Archaeology', 'Music', 'Near Eastern Studies', 'Latin American Studies', 'Gender and Sexuality Studies', 'Hellenic Studies', 'South Asian Studies', 'East Asian Studies') THEN 'humanities'
        WHEN department IN ('Politics', 'Psychology', 'Sociology', 'Economics', 'Anthropology', 'Public and International Affairs') THEN 'socialSciences'
        WHEN department IN ('Physics', 'Computer Science', 'Molecular Biology', 'Ecology and Evolutionary Biology', 'Geosciences', 'Mathematics') THEN 'science'
        WHEN department IN ('Chemical and Biological Engineering', 'Civil and Environmental Engineering', 'Electrical and Computer Engineering', 'Operations Research and Financial Engineering', 'Program in Applied and Computational Mathematics') THEN 'engineering'
        WHEN department IN ('Center for Information Technology Policy') THEN 'technology'
        WHEN department IN ('Program in Environmental Studies') THEN 'environmental'
        ELSE 'other'
    END as meta_category
FROM events
WHERE department IS NOT NULL;

-- Sample data for testing (optional)
-- INSERT OR IGNORE INTO events (event_id, title, description, start_date, time, location, department, url) VALUES
-- ('test-1', 'Sample Event 1', 'This is a sample event description', '2024-01-15', '14:00', 'Room 101', 'Computer Science', 'https://example.com/event1'),
-- ('test-2', 'Sample Event 2', 'Another sample event description', '2024-01-16', '15:30', 'Room 202', 'Physics', 'https://example.com/event2');
