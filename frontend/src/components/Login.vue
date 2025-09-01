<template>
  <div class="w-full max-w-md sm:max-w-sm mx-auto mt-10 p-6 border rounded shadow bg-white">
    <h2 class="text-xl font-bold mb-4 text-center">Login</h2>

    <form @submit.prevent="handleLogin" class="flex flex-col gap-4">
      <input
        v-model="username"
        type="text"
        placeholder="Username"
        class="w-full border p-2 rounded"
        required
      />
      <input
        v-model="password"
        type="password"
        placeholder="Password"
        class="w-full border p-2 rounded"
        required
      />
      <button
        type="submit"
        class="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
      >
        Log In
      </button>
      <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { api } from '../main.js'
import { useUserStore } from '../store/useUserStore'

const username = ref('')
const password = ref('')
const error = ref('')
const userStore = useUserStore()

const handleLogin = async () => {
  error.value = ''

  try {
    const res = await api.post('/login', {
      username: username.value,
      password: password.value
    })

    userStore.setUser(res.data.user)
  } catch (err) {
    if (err.response?.status === 401) {
      error.value = 'Invalid username or password'
    } else if (err.response?.status === 429) {
      error.value = 'Too many attempts. Try again later.'
    } else {
      error.value = 'Login failed. Try again.'
    }
  }
}
</script>