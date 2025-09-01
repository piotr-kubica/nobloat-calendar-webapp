<template>
  <div class="w-full max-w-3xl mx-auto px-4 sm:px-0">
    <!-- Month Navigation -->
    <div class="flex justify-between items-center mb-4">
      <button @click="prevMonth" class="px-2 py-1 bg-gray-300 rounded hover:bg-gray-400">←</button>
      <h2 class="text-xl font-bold">{{ currentMonthYear }}</h2>
      <button @click="nextMonth" class="px-2 py-1 bg-gray-300 rounded hover:bg-gray-400">→</button>
    </div>

    <!-- Calendar Grid -->
    <div class="grid grid-cols-7 gap-2">
      <div class="text-center font-semibold" v-for="day in weekDays" :key="day">{{ day }}</div>

      <div
        v-for="day in calendarDays"
        :key="day.date + '-' + day.day"
        @click="day.valid && selectDay(day.date)"
        class="w-full sm:w-16 h-14 sm:h-16 rounded flex flex-col items-center justify-center relative"
        :class="[
          day.valid ? 'cursor-pointer' : 'bg-gray-100 text-gray-400',
          isToday(day.date) ? 'border-2 border-blue-500' : 'border',
          day.valid && selectedDate === day.date ? 'bg-blue-100' : '',
          day.valid && !hasActivities(day.date) ? 'hover:bg-gray-50' : ''
        ]"
      >
        <!-- Inside your calendar cell -->
        <div class="text-center">
          <div v-if="hasActivities(day.date)">
            <!-- Dots (top 2) -->
            <div class="flex gap-1 justify-center mb-0.5">
              <template v-for="(activity, index) in visibleDots(day.date).top" :key="index">
                <span class="w-2 h-2 rounded-full" :class="dotColorClass(activity.type)"></span>
              </template>
            </div>

            <!-- "+n" or nothing -->
            <div class="text-xs font-semibold text-gray-600">
              <span v-if="visibleDots(day.date).remaining > 0">
                +{{ visibleDots(day.date).remaining }}
              </span>
            </div>

            <!-- Show day number only if remaining is 0 -->
            <div v-if="visibleDots(day.date).remaining === 0">
              <div class="font-medium">{{ day.day }}</div>
            </div>
          </div>

          <!-- If no activities, just show day -->
          <div v-else>
            <div class="font-medium">{{ day.day }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Activity Detail View -->
    <div v-if="selectedDate" class="mt-4 p-4 border rounded bg-gray-50">
      <h3 class="font-bold mb-2">Activities on {{ selectedDate }}</h3>
      <ul>
        <li
          v-for="(activity, index) in events[selectedDate]"
          :key="index"
          class="flex justify-between items-start gap-2 mb-2"
        >
          <div class="flex items-start gap-2">
            <span class="w-2 h-2 rounded-full mt-1" :class="dotColorClass(activity.type)"></span>
            <div>
              <div class="font-medium capitalize">{{ activity.title }}</div>
              <div v-if="activity.description" class="text-sm text-gray-500">{{ activity.description }}</div>
            </div>
          </div>
          <button
            class="text-red-500 text-sm hover:underline"
            @click="deleteActivity(selectedDate, index)"
          >
            Delete
          </button>
        </li>
      </ul>

      <!-- Add Activity Form -->
      <div class="mt-4">
        <h4 class="font-semibold mb-2">Add Activity</h4>
        <form @submit.prevent="addActivity">
          <div class="flex flex-col gap-2">
            <select v-model="newActivity.type" required class="border p-1 rounded">
              <option disabled value="">Select type</option>
              <option value="meeting">Meeting</option>
              <option value="event">Event</option>
              <option value="sport">Sport</option>
              <option value="note">Note</option>
            </select>

            <input
              v-model="newActivity.title"
              type="text"
              placeholder="Title"
              required
              class="border p-1 rounded"
              maxlength="100"
            />

            <textarea
              v-model="newActivity.description"
              placeholder="Description (optional)"
              maxlength="255"
              class="border p-1 rounded"
            ></textarea>

            <button
              type="submit"
              class="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 w-fit"
            >
              Add
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Monthly Summary -->
    <div class="mt-6 p-4 border rounded bg-gray-50">
      <h3 class="font-bold mb-2">Monthly Summary</h3>
      <ul>
        <li
          v-for="(type, index) in sortedActivityTypes"
          :key="index"
          class="flex items-center gap-2 mb-1"
        >
          <span class="w-2 h-2 rounded-full" :class="dotColorClass(type)"></span>
          <span class="capitalize">{{ type }}</span>:
          <span>{{ activitySummary[type] }} day<span v-if="activitySummary[type] > 1">s</span></span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useEventsStore } from '../store/useEventsStore'
import { storeToRefs } from 'pinia'

const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const store = useEventsStore()
const { eventsByDate } = storeToRefs(store)
const events = computed(() => store.eventsByDate)

const hasActivities = (date) => !!events.value[date]

const currentDate = ref(new Date())
const selectedDate = ref(null)

const year = computed(() => currentDate.value.getFullYear())
const month = computed(() => currentDate.value.getMonth() + 1)

watch([year, month], () => {
  store.fetchEventsForMonth(year.value, month.value)
}, { immediate: true })

const ALLOWED_TYPES = ['meeting', 'event', 'sport', 'note']

const todayStr = new Date().toISOString().split("T")[0];

const isToday = (dateStr) => {
  return dateStr === todayStr;
};

function validateActivity(activity) {
  if (!activity || typeof activity !== 'object') {
    throw new Error('Invalid activity format')
  }

  const title = (activity.title || '').trim()
  if (!title) {
    throw new Error('Title is required')
  }
  if (title.length > 100) {
    throw new Error('Title must be 100 characters or less')
  }

  const type = activity.type?.toLowerCase()
  if (!ALLOWED_TYPES.includes(type)) {
    throw new Error(`Invalid activity type: ${activity.type}`)
  }

  if (activity.description && activity.description.length > 255) {
    throw new Error('Description must be 255 characters or less')
  }

  return {
    ...activity,
    title,
    type,
    description: activity.description?.slice(0, 255) || ''
  }
}

const currentMonthYear = computed(() => {
  return currentDate.value.toLocaleDateString('default', { year: 'numeric', month: 'long' })
})

const newActivity = ref({
  type: '',
  title: '',
  description: ''
})

const addActivity = async () => {
  const { type, title, description } = newActivity.value;
  if (!type || !title) return;

  try {
    const activity = validateActivity({ type, title, description });
    await store.addEvent(selectedDate.value, activity);
    await store.fetchEventsForMonth(year.value, month.value, true);
    console.log(JSON.stringify(events.value[selectedDate.value], null, 2));
    newActivity.value = { type: '', title: '', description: '' };
  } catch (error) {
    console.error('Failed to add activity:', error);
  }
};

const deleteActivity = async (date, index) => {
  const activity = events.value[date]?.[index];
  if (!activity || !activity.id) return;

  try {
    await store.deleteEvent(activity.id, date);
    await store.fetchEventsForMonth(year.value, month.value, true);
    console.log(JSON.stringify(events.value[selectedDate.value], null, 2));
  } catch (error) {
    console.error('Failed to delete activity:', error);
  }
};

const visibleDots = (date) => {
  const acts = events.value[date] || [];
  const top = acts.slice(0, 2);
  const remaining = acts.length > 2 ? acts.length - 2 : 0;
  return { top, remaining };
};

const selectDay = (date) => {
  if (!date) return
  selectedDate.value = date
}

const dotColorClass = (type) => {
  const t = type.toLowerCase()
  return {
    meeting: 'bg-blue-500',
    event: 'bg-green-500',
    sport: 'bg-orange-500',
    note: 'bg-yellow-400'
  }[t] || 'bg-gray-300'
}

const activitySummary = computed(() => {
  const summary = {}

  for (const [date, activities] of Object.entries(events.value)) {
    const dateMonth = `${year.value}-${String(month.value).padStart(2, '0')}`
    if (!date.startsWith(dateMonth)) continue

    const seen = new Set()
    for (const activity of activities) {
      seen.add(activity.type)
    }

    for (const type of seen) {
      summary[type] = (summary[type] || 0) + 1
    }
  }

  return summary
})

const sortedActivityTypes = computed(() => {
  return Object.keys(activitySummary.value).sort()
})

const calendarDays = computed(() => {
  const date = new Date(year.value, month.value - 1, 1)
  // shift getDay() so Monday = 0, Tuesday = 1, ..., Sunday = 6
  const startDay = (date.getDay() + 6) % 7
  const days = []
  const lastDate = new Date(year.value, month.value, 0).getDate()

  for (let i = 0; i < startDay; i++) {
    days.push({ day: '', date: '', valid: false }) // ⛔️ placeholder
  }

  for (let i = 1; i <= lastDate; i++) {
    const formatted = `${year.value}-${String(month.value).padStart(2, '0')}-${String(i).padStart(2, '0')}`
    days.push({ day: i, date: formatted, valid: true }) // ✅ real day
  }

  return days
})

const prevMonth = () => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(currentDate.value.getMonth() - 1)
  currentDate.value = newDate
}

const nextMonth = () => {
  const newDate = new Date(currentDate.value)
  newDate.setMonth(currentDate.value.getMonth() + 1)
  currentDate.value = newDate
}
</script>