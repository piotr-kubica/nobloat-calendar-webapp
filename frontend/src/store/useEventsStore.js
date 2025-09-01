import { defineStore } from 'pinia'
import { api } from '../main.js'

export const useEventsStore = defineStore('events', {
  state: () => ({
    eventsByDate: {},
  }),
  actions: {
    async fetchEventsForMonth(year, month, force = false) {
      const key = `${year}-${String(month).padStart(2, '0')}`;

      if (force) {
        // Remove all dates for that month to trigger reactivity
        for (const date in this.eventsByDate) {
          if (date.startsWith(key)) {
            delete this.eventsByDate[date];
          }
        }
      } else {
        if (Object.keys(this.eventsByDate).some(date => date.startsWith(key))) return;
      }

      try {
        const res = await api.get(`/activities/${key}`)
        this.eventsByDate = {
          ...this.eventsByDate,
          ...res.data,
        };
      } catch (err) {
        console.error('Error loading events:', err);
      }
    },

    clearEvents() {
      this.eventsByDate = {}
      this.eventsLoadedForMonth = ''
    },

    async addEvent(date, activity) {
      try {
        await api.post('/activities', {
          date,
          ...activity
        });
      } catch (err) {
        console.error('Error adding event:', err);
      }
    },

    async deleteEvent(id, date) {
      try {
        await api.delete(`/activities/${id}`);
      } catch (err) {
        console.error('Error deleting event:', err);
      }
    }

  },
})