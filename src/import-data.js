// Data import script for Princeton Academic Events
// This script imports events from our JSON files into the D1 database

import { readFileSync } from 'fs';

export default {
  async fetch(request, env, ctx) {
    // Only allow POST requests for data import
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    try {
      const { events } = await request.json();
      
      if (!events || !Array.isArray(events)) {
        return new Response(JSON.stringify({ error: 'Invalid events data' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      let imported = 0;
      let errors = 0;

      for (const event of events) {
        try {
          // Get department ID
          const deptResult = await env.DB.prepare(
            'SELECT id FROM departments WHERE name = ?'
          ).bind(event.department).first();

          if (!deptResult) {
            console.warn(`Department not found: ${event.department}`);
            errors++;
            continue;
          }

          // Check if event already exists
          const existingEvent = await env.DB.prepare(
            'SELECT id FROM events WHERE event_id = ?'
          ).bind(event.id).first();

          if (existingEvent) {
            // Update existing event
            await env.DB.prepare(`
              UPDATE events SET
                title = ?,
                description = ?,
                start_date = ?,
                end_date = ?,
                time = ?,
                location = ?,
                event_type = ?,
                source_url = ?,
                source_name = ?,
                tags = ?,
                updated_at = CURRENT_TIMESTAMP
              WHERE event_id = ?
            `).bind(
              event.title,
              event.description || '',
              event.start_date,
              event.end_date,
              event.time || '',
              event.location || 'TBD',
              event.event_type,
              event.source_url || '',
              event.source_name || '',
              JSON.stringify(event.tags || []),
              event.id
            ).run();
          } else {
            // Insert new event
            await env.DB.prepare(`
              INSERT INTO events (
                event_id, title, description, start_date, end_date, time,
                location, event_type, department_id, source_url, source_name, tags
              ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `).bind(
              event.id,
              event.title,
              event.description || '',
              event.start_date,
              event.end_date,
              event.time || '',
              event.location || 'TBD',
              event.event_type,
              deptResult.id,
              event.source_url || '',
              event.source_name || '',
              JSON.stringify(event.tags || [])
            ).run();
          }

          imported++;
        } catch (error) {
          console.error(`Error importing event ${event.id}:`, error);
          errors++;
        }
      }

      return new Response(JSON.stringify({
        success: true,
        imported,
        errors,
        total: events.length
      }), {
        headers: { 'Content-Type': 'application/json' }
      });

    } catch (error) {
      console.error('Import error:', error);
      return new Response(JSON.stringify({ error: 'Import failed' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};
