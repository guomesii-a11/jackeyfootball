<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

<template>
  <section class="flex items-center justify-center py-24">
    <h1
      class="text-[64px] font-extrabold leading-[1.1] bg-gradient-to-r from-forward via-orange-400 to-gold bg-clip-text text-transparent text-center tracking-tight"
    >
      {{ t('hero.title') }}
    </h1>
  </section>
</template>
