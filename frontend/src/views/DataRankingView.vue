<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { getPlayersWithStats } from '@/api/client'
import { clubNameOf } from '@/constants'
import type { PlayerWithStats } from '@/types'

const { t, locale } = useI18n()

const players = ref<PlayerWithStats[]>([])
const loading = ref(true)
const error = ref('')
const sel = ref('goals')

const metrics = [
  { key: 'goals', icon: '⚽' },
  { key: 'assists', icon: '🅰️' },
  { key: 'appearances', icon: '📅' },
  { key: 'minutes_played', icon: '⏱️' },
  { key: 'shots_total', icon: '🎯' },
  { key: 'shots_on_target', icon: '🎯' },
  { key: 'pass_accuracy', icon: '🎯' },
  { key: 'key_passes', icon: '🅰️' },
  { key: 'tackles', icon: '🛡️' },
  { key: 'interceptions', icon: '🛡️' },
  { key: 'clearances', icon: '🧹' },
  { key: 'blocks', icon: '🧱' },
  { key: 'saves', icon: '🧤' },
  { key: 'clean_sheets', icon: '🧤' },
  { key: 'goals_conceded', icon: '⚽' },
  { key: 'dribbles_completed', icon: '💨' },
  { key: 'aerial_duels_won', icon: '📐' },
]

function nameOf(p: PlayerWithStats) {
  return locale.value === 'zh' ? p.name : p.name_en || p.name
}

// 全体球员按当前指标统一降序排名（不再按位置分组）
const ranked = computed(() => {
  const key = sel.value
  const sorted = [...players.value].sort((a, b) => {
    const av = a.stats ? Number((a.stats as any)[key] ?? 0) : 0
    const bv = b.stats ? Number((b.stats as any)[key] ?? 0) : 0
    return bv - av
  })
  return sorted
})

const maxVal = computed(() => {
  if (!ranked.value.length) return 1
  const first = ranked.value[0]
  return first.stats ? Number((first.stats as any)[sel.value] ?? 0) : 0
})

function widthOf(p: PlayerWithStats): number {
  const v = p.stats ? Number((p.stats as any)[sel.value] ?? 0) : 0
  if (!maxVal.value) return 0
  return Math.max(2, (v / maxVal.value) * 100)
}

function valueOf(p: PlayerWithStats): number {
  return p.stats ? Number((p.stats as any)[sel.value] ?? 0) : 0
}

function selectMetric(m: { key: string }) {
  sel.value = m.key
}

onMounted(async () => {
  try {
    players.value = await getPlayersWithStats()
  } catch (e) {
    error.value = '加载数据失败'
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="mx-auto max-w-6xl px-4 py-8">
    <header class="mb-8">
      <h1 class="text-4xl font-extrabold text-white">{{ t('data.title') }}</h1>
      <p class="mt-2 text-base text-white/80">{{ t('data.subtitle') }}</p>
    </header>

    <div v-if="loading" class="py-20 text-center text-slate-400">{{ t('data.loading') }}</div>
    <div v-else-if="error" class="py-20 text-center text-red-500">{{ error }}</div>

    <template v-else>
      <!-- 指标切换 -->
      <div class="mb-6 flex flex-wrap gap-2">
        <button
          v-for="m in metrics"
          :key="m.key"
          @click="selectMetric(m)"
          :class="[
            'rounded-full px-4 py-1.5 text-sm font-medium transition',
            m.key === sel
              ? 'bg-indigo-600 text-white'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200',
          ]"
        >
          {{ m.icon }} {{ t('dataMetrics.' + m.key) }}
        </button>
      </div>

      <!-- 全体统一排名 -->
      <div class="rounded-2xl bg-white p-4 shadow-sm sm:p-6">
        <ol class="space-y-2">
          <li
            v-for="(p, i) in ranked"
            :key="p.id"
            class="flex items-center gap-3"
          >
            <span
              :class="[
                'w-8 shrink-0 text-center text-sm font-bold',
                i < 3 ? 'text-indigo-600' : 'text-slate-400',
              ]"
            >{{ i + 1 }}</span>
            <img
              :src="p.image_url"
              :alt="p.name_en"
              class="h-9 w-9 shrink-0 rounded-full bg-slate-100 object-cover"
              @error="($event.target as HTMLImageElement).style.visibility = 'hidden'"
            />
            <div class="min-w-0 flex-1">
              <div class="mb-1 flex items-baseline justify-between gap-2">
                <span class="truncate font-medium text-slate-800">{{ nameOf(p) }}</span>
                <span class="shrink-0 text-sm tabular-nums text-slate-500">
                  {{ valueOf(p) }} · {{ clubNameOf(p.current_club, locale) }}
                </span>
              </div>
              <div class="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-indigo-400 to-indigo-600"
                  :style="{ width: widthOf(p) + '%' }"
                ></div>
              </div>
            </div>
          </li>
        </ol>
      </div>
    </template>
  </div>
</template>
