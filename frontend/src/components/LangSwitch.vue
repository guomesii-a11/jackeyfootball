<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

function toggle() {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
  localStorage.setItem('jf_lang', locale.value)
}
</script>

<template>
  <button
    class="glass-soft rounded-full px-3 py-1.5 text-sm font-bold flex items-center gap-1 transition-colors hover:border-white/30"
    @click="toggle"
  >
    <span :class="locale === 'zh' ? 'text-gold' : 'text-muted'">中</span>
    <span class="text-muted">/</span>
    <span :class="locale === 'en' ? 'text-gold' : 'text-muted'">EN</span>
  </button>
</template>
