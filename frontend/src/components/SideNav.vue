<script setup lang="ts">
import { Trophy, BarChart3, Users } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const cards = [
  { to: '/players', icon: Trophy, titleKey: 'nav.power', descKey: 'sideNav.powerDesc', color: '#FF5A36' },
  { to: '/data', icon: BarChart3, titleKey: 'nav.data', descKey: 'sideNav.dataDesc', color: '#1FB6C9' },
  { to: '/compare', icon: Users, titleKey: 'nav.compare', descKey: 'sideNav.compareDesc', color: '#9B59F6' },
]
</script>

<template>
  <aside class="flex flex-col gap-6 h-full">
    <RouterLink
      v-for="c in cards"
      :key="c.to"
      :to="c.to"
      class="group glass rounded-2xl p-7 flex items-center gap-5 transition-all duration-200 hover:-translate-y-1"
      :style="{ borderColor: c.color + '55' }"
    >
      <div
        class="w-16 h-16 rounded-xl flex items-center justify-center shrink-0"
        :style="{ background: c.color + '22', color: c.color }"
      >
        <component :is="c.icon" :size="28" />
      </div>
      <div>
        <div class="font-bold text-2xl">{{ t(c.titleKey) }}</div>
        <div class="text-base text-muted">{{ t(c.descKey) }}</div>
      </div>
    </RouterLink>
  </aside>
</template>
