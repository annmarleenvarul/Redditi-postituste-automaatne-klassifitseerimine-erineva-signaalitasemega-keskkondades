<template>
    <header class="header">
        <div class="logo">jungler.ai</div>
        <input :value="modelValue" type="text" placeholder="HubSpot" @input="$emit('update:modelValue', $event.target.value)" @keyup.enter="$emit('search')" />
    <button @click="$emit('search')">Otsi</button>

    <span v-if="total !== null" class="total">{{ total }} postitust</span>
    </header>
</template>

<script setup>
defineProps({
    modelValue: String, 
    total:      Number, 
})

defineEmits(['update:modelValue', 'search'])
</script>

<style scoped>
.header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 10px;
    border-bottom: 1px solid var(--border);
    background: var(--card);
    position: sticky;
    top: 0;
    z-index: 10;
    border-radius: 8px;
}

.logo {
    font-size: 18px;
    font-weight: 600;
    color: var(--blue);
    white-space: nowrap;
}

input {
    flex: 1;
    padding: 7px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--background);
    font-family: inherit;
    font-size: 16px;
    outline: none;
}
input:focus {
    border-color: var(--blue);
}

button {
    padding: 7px 16px;
    background: var(--blue);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: inherit;
    font-size: 16px;
    cursor: pointer;
    white-space: nowrap;
}
button:hover {
    opacity: 0.9;
}

.total {
    font-size: 15px;
    color: var(--gray);
    white-space: nowrap;
}
</style>