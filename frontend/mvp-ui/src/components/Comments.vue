<template>
    <div class="comment">

        <div class="comment-header">
        <span class="comment-author">{{ comment.author || '[deleted]' }}</span>
        <span class="comment-score">üleshääli: {{ comment.score }}</span>
        <button class="comment-collapse" @click="collapsed = !collapsed">
            {{ collapsed ? '[+]' : '[-]' }}
        </button>
        </div>

        <template v-if="!collapsed">
        <div class="comment-body" v-html="highlightFn(comment.body, highlightQuotes)"></div>

        <div class="replies">
            <Comments
            v-for="childComment in comment.children"
            :key="childComment.id"
            :comment="childComment"
            :highlight-quotes="highlightQuotes"
            :highlight-fn="highlightFn"
            />
        </div>
        </template>

    </div>
</template>

<script setup>
import { ref } from 'vue'

const collapsed = ref(false)

defineProps({
    comment: Object,
    highlightQuotes: Array,
    highlightFn: Function,
})
</script>

<style>
.comment {
    border-left: 2px solid var(--border);
    padding-left: 10px;
    margin-top: 8px;
}

.comment-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 3px;
}

.comment-author {
    font-size: 14px;
    font-weight: 600;
    color: var(--blue);
}

.comment-score {
    font-size: 13px;
    color: var(--gray);
}

.comment-collapse {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 13px;
    color: var(--gray);
    font-family: monospace;
    padding: 0;
}
.comment-collapse:hover { color: var(--text); }

.comment-body {
    font-size: 15px;
    line-height: 1.6;
    color: #333;
    word-break: break-word;
}

.replies {
    margin-left: 12px;
}
</style>