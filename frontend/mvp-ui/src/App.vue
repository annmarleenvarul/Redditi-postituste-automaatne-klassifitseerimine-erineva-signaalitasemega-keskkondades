<template>
  <div class="app">

  <AppHeader v-model="searchQuery" :total="total" @search="fetchData" />

    <div class="layout">

      <AppSidebar
        :subreddits="stats?.subreddits || []"
        :active-subreddit="activeSubreddit"
        :filters="filters"
        :stats="stats"
        @toggle-subreddit="toggleSubreddit"
        @toggle-filter="toggleFilter"
      />

      <main class="content">

        <div v-if="noData" class="no-data">
          <p>Andmed puuduvad.</p>
        </div>

        <div v-if="loading" class="status">Laeb...</div>

        <template v-if="!loading && !noData">
          <ThreadCard
            v-for="thread in threads"
            :key="thread.id"
            :thread="thread"
            :is-expanded="expandedId === thread.id"
            :detail="expandedId === thread.id ? threadDetail : null"
            :detail-loading="detailLoading"
            :highlight-fn="highlightText"
            :build-comment-tree="buildCommentTree"
            @toggle="toggleThread"
          />
          <button v-if="page < totalPages" class="load-more" @click="loadMore">
            Lae veel
          </button>
        </template>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppHeader from './components/Header.vue'
import AppSidebar from './components/Side.vue'
import ThreadCard from './components/Thread.vue'

const API_URL = 'http://localhost:8000'

const SUPPORTED_QUERY = 'hubspot'

const searchQuery = ref('HubSpot')      
const activeSubreddit = ref(null)       
const loading = ref(false)              
const noData = ref(false)               

const threads = ref([])                 
const stats = ref(null)                 
const page = ref(1)                     
const totalPages = ref(1)              

const expandedId = ref(null)           
const threadDetail = ref(null)         
const detailLoading = ref(false)       
const total = ref(null)

const filters = reactive({
  negative: false,
  positive: false,
  neutral: false,
  product_feedback: false,
  bug_report: false,
  limitation: false,
  comparison: false,
  churn_risk: false,
  purchase_intent: false,
})


function buildQueryParams(pageNumber = 1) {
  const params = new URLSearchParams({ tab: 'all', page: pageNumber, page_size: 10 })

  if (activeSubreddit.value) {
    params.set('subreddit', activeSubreddit.value)
  }

  if (filters.product_feedback) {
    params.set('product_feedback', 'true')
  }

  const selectedSentiments = ['negative', 'positive', 'neutral'].filter(key => filters[key])
  if (selectedSentiments.length >= 1) {
    params.set('sentiment', selectedSentiments.join(','))
}

  const selectedLabels = ['bug_report', 'limitation', 'comparison', 'churn_risk', 'purchase_intent'].filter(key => filters[key])
  if (selectedLabels.length > 0) {
    params.set('labels', selectedLabels.join(','))
  }

  return params.toString()
}

async function fetchData() {
  const query = searchQuery.value.trim().toLowerCase()

  if (query !== SUPPORTED_QUERY) {
    noData.value = true
    threads.value = []
    stats.value = null
    return
  }

  noData.value = false
  loading.value = true
  page.value = 1

  try {
    const threadsUrl = `${API_URL}/api/threads?${buildQueryParams(1)}`
    const statsUrl = `${API_URL}/api/stats${activeSubreddit.value ? '?subreddit=' + activeSubreddit.value : ''}`

    const [threadsResponse, statsResponse] = await Promise.all([
      fetch(threadsUrl),
      fetch(statsUrl)
    ])

    const threadsData = await threadsResponse.json()
    const statsData = await statsResponse.json()

    threads.value = threadsData.threads
    totalPages.value = threadsData.pages
    total.value = threadsData.total 

    stats.value = statsData

  } catch (error) {
    console.error('Andmete laadimine ebaõnnestus:', error)
  }

  loading.value = false
}

async function loadMore() {
  page.value++

  const response = await fetch(`${API_URL}/api/threads?${buildQueryParams(page.value)}`)
  const data = await response.json()

  threads.value = [...threads.value, ...data.threads]
}

async function toggleThread(thread) {
  if (expandedId.value === thread.id) {
    expandedId.value = null
    threadDetail.value = null
    return
  }

  expandedId.value = thread.id
  threadDetail.value = null
  detailLoading.value = true

  try {
    const response = await fetch(`${API_URL}/api/thread/${thread.id}`)
    threadDetail.value = await response.json()
  } catch (error) {
    console.error('Postituse laadimine ebaõnnestus:', error)
  }

  detailLoading.value = false
}

function toggleSubreddit(name) {
  if (activeSubreddit.value === name) {
    activeSubreddit.value = null
  } else {
    activeSubreddit.value = name
  }
  fetchData()
}

function toggleFilter(key) {
  filters[key] = !filters[key]
  fetchData()
}


function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function escapeRegex(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

function formatInline(text) {
  text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  text = text.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
  text = text.replace(/_(.*?)_/g, '<em>$1</em>')
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>')
  return text
}

function parseMarkdown(text) {
  if (!text) return ''

  const lines = text.split('\n')
  const outputLines = []
  let currentListType = null 

  function closeList() {
    if (currentListType === 'ul') outputLines.push('</ul>')
    if (currentListType === 'ol') outputLines.push('</ol>')
    currentListType = null
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()

    const headingMatch = line.match(/^(#{1,3})\s+(.+)/)
    if (headingMatch) {
      closeList()
      const level = headingMatch[1].length
      outputLines.push(`<h${level}>${formatInline(headingMatch[2])}</h${level}>`)
      continue
    }

    const numberedMatch = line.match(/^\d+\.\s+(.+)/)
    if (numberedMatch) {
      if (currentListType !== 'ol') { closeList(); outputLines.push('<ol>'); currentListType = 'ol' }
      outputLines.push(`<li>${formatInline(numberedMatch[1])}</li>`)
      continue
    }

    const bulletMatch = line.match(/^[-*+]\s+(.+)/)
    if (bulletMatch) {
      if (currentListType !== 'ul') { closeList(); outputLines.push('<ul>'); currentListType = 'ul' }
      outputLines.push(`<li>${formatInline(bulletMatch[1])}</li>`)
      continue
    }

    const quoteMatch = line.match(/^>\s*(.*)/)
    if (quoteMatch) {
      closeList()
      outputLines.push(`<blockquote>${formatInline(quoteMatch[1])}</blockquote>`)
      continue
    }

    closeList()
    outputLines.push(line ? `<p>${formatInline(line)}</p>` : '<br>')
  }

  closeList()
  return outputLines.join('\n')
}

function highlightText(text, quotes) {
  if (!text) return ''

  let html = parseMarkdown(text)

  if (!quotes || quotes.length === 0) return html

  for (const quote of quotes) {
    if (!quote || quote.length < 8) continue

    try {
      const words = quote.trim().split(/\s+/)

      for (let length = words.length; length >= Math.min(4, words.length); length--) {
        const pattern = words
          .slice(0, length)
          .map(word => escapeRegex(escapeHtml(word)))
          .join('[\\s\\S]{0,10}')

        const highlighted = html.replace(
          new RegExp(pattern, 'gi'),
          match => `<mark class="hl">${match}</mark>`
        )

        if (highlighted !== html) {
          html = highlighted
          break
        }
      }
    } catch (error) {
    }
  }

  return html
}

function buildCommentTree(comments) {
  if (!comments) return []

  const commentMap = {}
  for (const comment of comments) {
    commentMap[comment.id] = { ...comment, children: [] }
  }

  const rootComments = []
  for (const comment of comments) {
    const parentId = comment.parent_id?.replace('t1_', '').replace('t3_', '')

    if (commentMap[parentId]) {
      commentMap[parentId].children.push(commentMap[comment.id])
    } else {
      rootComments.push(commentMap[comment.id])
    }
  }

  return rootComments
}

onMounted(fetchData)
</script>

<style>
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --background: #f4f4f5;
  --card: #fff;
  --border: #e4e4e7;
  --text: #111;
  --gray: #71717a;
  --blue: #466ee5;
  --red: #dc2626;
  --green: #16a34a;
  --orange: #d97706;
  --border-radius: 10px;
}

body {
  font-family: sans-serif;
  background: var(--background);
  color: var(--text);
  font-size: 17px;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.layout {
  display: flex;
  flex: 1;
}

.content {
  flex: 1;
  padding: 16px 0 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.no-data {
  padding: 60px 20px;
  text-align: center;
  color: var(--gray);
}

.status {
  padding: 40px;
  text-align: center;
  color: var(--gray);
}

.load-more {
  width: 100%;
  padding: 10px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--border-radius);
  cursor: pointer;
  font-family: inherit;
  font-size: 15px;
  color: var(--text);
}
.load-more:hover {
  background: var(--background);
}

mark.hl {
  background: #fef08a;
  border-radius: 2px;
  padding: 0 1px;
}

blockquote {
  border-left: 3px solid var(--border);
  padding-left: 10px;
  color: var(--gray);
  font-style: italic;
  margin: 6px 0;
}

.post-body ul, .post-body ol,
.comment-body ul, .comment-body ol {
  padding-left: 20px;
  margin: 4px 0;
}
.post-body li, .comment-body li {
  margin: 2px 0;
}
</style>