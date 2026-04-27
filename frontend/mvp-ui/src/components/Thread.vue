<template>
    <div class="wrapper">

        <div class="card">
        <div class="top">
            <span class="meta">
            /r/{{ thread.subreddit }} · {{ thread.time_ago }} · {{ thread.num_comments }} kommentaari
            </span>
            <span class="badge">Relevantsus: {{ thread.relevancy_score }}</span>
        </div>

        <div class="title">{{ thread.title }}</div>

        <div class="labels">
            <span class="label sentiment-badge" :class="thread.sentiment"> {{ translateLabel(thread.sentiment) }} </span>
            <span v-for="label in thread.labels" :key="label" class="label" :class="labelClass(label)" >
            {{ translateLabel(label) }}
            </span>
        </div>

        <div class="summary" v-if="thread.summary_et">
            <strong>LLM kokkuvõte:</strong> {{ thread.summary_et }}
        </div>

        <div class="footer">
            <span>üleshääli: {{ thread.score }}</span>
            <span class="sep">·</span>
            <span>Tagasiside: {{ thread.product_feedback ? 'jah' : 'ei' }}</span>
            <span class="sep">·</span>
            <button @click="$emit('toggle', thread)"> {{ isExpanded ? 'Sule' : 'Ava' }} </button>
            <a :href="thread.url" target="_blank" class="reddit-link" @click.stop>Link</a>
        </div>

    </div>

    <div class="expanded" v-if="isExpanded">

        <div class="loading-msg" v-if="detailLoading">Laeb...</div>

        <template v-else-if="detail">

        <div class="highlights" v-if="detail.highlights?.length">
            <div class="highlights-title">Olulisem</div>
            <div v-for="(highlight, index) in detail.highlights" :key="index" class="highlight-item">
            <em>"{{ highlight.quote }}"</em>
            <span class="aspect">{{ highlight.aspect }}</span>
            </div>
        </div>

        <div
            class="post-body"
            v-if="detail.selftext"
            v-html="highlightFn(detail.selftext, detail.highlight_quotes)"
        ></div>
        <div v-if="detail.comments?.length">
            <div class="comments-title">Kommentaarid ({{ detail.comments.length }})</div>
            <Comments
                v-for="comment in buildCommentTree(detail.comments)"
                :key="comment.id"
                :comment="comment"
                :highlight-quotes="detail.highlight_quotes"
                :highlight-fn="highlightFn"
            />
        </div>

        </template>
    </div>

    </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import Comments from './Comments.vue'

const labelTranslations = {
    negative: 'Negatiivne',
    positive: 'Positiivne',
    neutral:  'Neutraalne',
    bug_report:'Vearaport',
    limitation:'Piirang',
    comparison:'Võrdlus',
    churn_risk:'Lahkumisrisk',
    purchase_intent: 'Ostukavatsus',
    pricing: 'Hinnastus',
    usability: 'Kasutatavus',
    performance: 'Jõudlus',
    integration: 'Integratsioon',
    automation: 'Automatiseerimine',
    API: 'API',
    AI: 'Tehisintellekt',
    onboarding: 'Kasutuselevõtt',
    support:'Tugi',
    feature_request:'Funktsioonisoov',
    reporting: 'Aruandlus',
    best_practices: 'Parimad praktikad',
    data_quality:'Andmekvaliteet',
    data_management:'Andmehaldus',
    workflow_management:'Töövoo haldus',
}

const autoTranslated = reactive({})

function translateLabel(label) {
    return labelTranslations[label] || autoTranslated[label] || label.replaceAll('_', ' ')
}

async function fetchTranslation(label) {
    if (labelTranslations[label] || autoTranslated[label]) return

    const readable = label.replaceAll('_', ' ')
    try {
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=et&dt=t&q=${encodeURIComponent(readable)}`
        const response = await fetch(url)
        const data = await response.json()
        autoTranslated[label] = data[0][0][0]
    } catch {
        autoTranslated[label] = readable
    }
}

function labelClass(label) {
    return label.replaceAll('_', '-').toLowerCase()
}

const props = defineProps(['thread', 'isExpanded', 'detail', 'detailLoading', 'highlightFn', 'buildCommentTree'])



watch(() => props.thread.labels, (labels) => {
    if (!labels) return
    for (const label of labels) {
        if (!labelTranslations[label]) {
            fetchTranslation(label)
        }
    }
}, { immediate: true })</script>

<style scoped>
.wrapper {
    display: flex;
    flex-direction: column;
}

.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--border-radius);
    padding: 14px 16px;
}

.wrapper:has(.expanded) .card {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
    border-bottom-color: transparent;
}

.top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}

.meta  { font-size: 13px; color: var(--gray); }
.badge { font-size: 13px; color: var(--gray); background: var(--background); border: 1px solid var(--border); padding: 1px 6px; border-radius: 4px; }

.sentiment-badge { font-size: 13px; font-weight: 500; padding: 1px 8px; border-radius: 4px; border: 1px solid; }
.sentiment-badge.negative { background: #fef2f2; color: var(--red); border-color: #fecaca; }
.sentiment-badge.positive { background: #f0fdf4; color: var(--green); border-color: #bbf7d0; }
.sentiment-badge.neutral  { background: #fefce8; color: #a16207;    border-color: #fde047; }

.title {
    font-size: 16px;
    font-weight: 500;
    line-height: 1.4;
    margin-bottom: 8px;
}

.labels {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 8px;
    text-transform: capitalize
}

.label { font-size: 13px; padding: 1px 7px; border-radius: 4px; border: 1px solid #d1d5db; background: #f9fafb; color: #374151; }
.label.bug-report { background: #fffbeb; color: var(--orange); border-color: #fde68a; }
.label.limitation { background: #eef2ff; color: var(--blue); border-color: #c7d2fe; }
.label.comparison { background: #fff7ed; color: #c2410c; border-color: #fed7aa; }
.label.churn-risk { background: #fef2f2; color: var(--red); border-color: #fecaca; }
.label.purchase-intent { background: #f0fdf4; color: var(--green); border-color: #bbf7d0; }

.summary {
    font-size: 14px;
    line-height: 1.65;
    color: #374151;
    border-left: 3px solid var(--blue);
    padding: 8px 12px;
    background: #f5f5ff;
    border-radius: 0 6px 6px 0;
    margin-bottom: 12px;
}

.footer {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--gray);
    flex-wrap: wrap;
}
.footer button {
    background: none;
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 13px;
    font-family: inherit;
    color: var(--blue);
    cursor: pointer;
}
.footer button:hover { background: #eef2ff; }

.reddit-link { font-size: 13px; color: #ff4500; text-decoration: none; font-weight: 500; }
.reddit-link:hover { text-decoration: underline; }

.expanded {
    background: var(--card);
    border: 1px solid var(--border);
    border-top: none;
    border-bottom-left-radius: var(--border-radius);
    border-bottom-right-radius: var(--border-radius);
    padding: 16px;
}

.loading-msg { color: var(--gray); font-size: 15px; }

.highlights {
    background: #fefce8;
    border: 1px solid #fde047;
    border-radius: 6px;
    padding: 10px 12px;
    margin-bottom: 14px;
    display: flex;
    flex-direction: column;
    gap: 5px;
}
.highlights-title { font-size: 13px; font-weight: 600; color: #854d0e; }
.highlight-item { display: flex; gap: 8px; align-items: baseline; font-size: 14px; }
.aspect { font-size: 12px; font-weight: 600; text-transform: uppercase; color: #a16207; }

.post-body {
    background: var(--background);
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 15px;
    line-height: 1.6;
    color: #333;
    margin-bottom: 14px;
    word-break: break-word;
    }

.comments-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--gray);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 12px 0 6px;
}
</style>