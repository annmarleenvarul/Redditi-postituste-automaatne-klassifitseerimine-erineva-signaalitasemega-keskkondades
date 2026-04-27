<template>
  <aside>
    <div class="box">
      <div class="title">Alamfoorumid</div>
      <div
        v-for="subreddit in subreddits"
        :key="subreddit.name"
        class="sub-item"
        :class="{ active: activeSubreddit === subreddit.name }"
        @click="$emit('toggle-subreddit', subreddit.name)"
      >
        <span>/r/{{ subreddit.name }}</span>
        <div class="bar-track">
          <div class="bar" :style="{ width: subreddit.pct + '%' }"></div>
        </div>
      </div>
    </div>

    <div class="box">
      <div class="title">Filtrid</div>
      <div v-for="filter in filterList" :key="filter.key" class="row">
        <span>{{ filter.label }}</span>
        <div
          class="toggle"
          :class="{ on: filters[filter.key] }"
          @click="$emit('toggle-filter', filter.key)"
        >
          <div class="knob"></div>
        </div>
      </div>
    </div>

    <div class="box" v-if="stats">
      <div class="title">Alamfoorumi meelestatus</div>
      <div v-for="sentiment in sentiments" :key="sentiment.key" class="row">
        <div class="bar-track">
          <div class="bar" :class="sentiment.key" :style="{ width: stats[sentiment.pct] + '%' }"></div>
        </div>
        <span class="pct">{{ stats[sentiment.pct] }}%</span>
      </div>
    </div>

  </aside>
</template>

<script setup>
defineProps({
  subreddits: { type: Array, default: () => [] },
  activeSubreddit: { type: String, default: null },
  filters: { type: Object, required: true },
  stats: { type: Object, default: null },
})


const filterList = [
  { key: 'negative', label: 'Negatiivne' },
  { key: 'positive', label: 'Positiivne' },
  { key: 'neutral', label: 'Neutraalne' },
  { key: 'product_feedback', label: 'Tootetagasiside' },
  { key: 'bug_report', label: 'Vea raport' },
  { key: 'limitation', label: 'Piirang' },
  { key: 'comparison', label: 'Võrdlus' },
  { key: 'churn_risk', label: 'Lahkumisrisk' },
  { key: 'purchase_intent', label: 'Ostukavatsus' },
]

const sentiments = [
  { key: 'negative', pct: 'negative_pct' },
  { key: 'positive', pct: 'positive_pct' },
  { key: 'neutral',  pct: 'neutral_pct' },
]
</script>

<style scoped>
aside {
  width: 210px;
  min-width: 210px;
  padding: 16px 12px 16px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.box {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--border-radius);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title {
  font-size: 15px;
  font-weight: bold;
  letter-spacing: 0.07em;
  color: var(--gray);
  
}

.sub-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 6px;
  font-size: 14px;
  text-transform: lowercase
}
.sub-item:hover { background: var(--background); }
.sub-item.active { background: #ede9fe; }

.bar-track {
  flex: 1;
  height: 3px;
  background: var(--border);
  border-radius: 2px;
}
.bar {
  height: 3px;
  background: var(--blue);
  border-radius: 2px;
}
.bar.negative { background: var(--red); }
.bar.positive  { background: var(--green); }
.bar.neutral   { background: #fde047; }

.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  font-size: 15px;
}

.toggle {
  width: 32px;
  height: 17px;
  background: var(--border);
  border-radius: 9px;
  cursor: pointer;
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}
.toggle.on { background: var(--blue); }

.knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 13px;
  height: 13px;
  background: #fff;
  border-radius: 50%;
  transition: left 0.2s;
}
.toggle.on .knob { left: 17px; }

.pct {
  font-size: 13px;
  color: var(--gray);
}
</style>