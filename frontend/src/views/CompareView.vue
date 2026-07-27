<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import RadarCompare from '@/components/RadarCompare.vue'
import { getPlayersCompare } from '@/api/client'
import type { PlayerDetail, Position } from '@/types'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

const all = ref<PlayerDetail[]>([])
const loading = ref(true)
const error = ref('')

// 自定义自选模式：用户手动勾选的球员 id（可跨位置）
const customIds = ref<number[]>([])
const search = ref('')

// 是否处于"自定义自选"模式
const isCustom = computed(() => customIds.value.length > 0)

// 最终传给雷达图的球员集合（只有用户勾选后才显示，默认空白）
const radarPlayers = computed<PlayerDetail[]>(() => {
  return all.value.filter((p) => customIds.value.includes(p.id))
})

// 搜索候选
const available = computed<PlayerDetail[]>(() => {
  const kw = search.value.trim().toLowerCase()
  return all.value
    .filter((p) => (p.name_en || '').toLowerCase().includes(kw) || p.name.toLowerCase().includes(kw))
    .slice(0, 8)
})

function nameOf(p: PlayerDetail) {
  return locale.value === 'en' ? p.name_en || p.name : p.name
}

function playerById(id: number) {
  return all.value.find((x) => x.id === id)!
}

function toggleCustom(p: PlayerDetail) {
  const i = customIds.value.indexOf(p.id)
  if (i >= 0) {
    customIds.value.splice(i, 1)
  } else if (customIds.value.length < 4) {
    customIds.value.push(p.id)
  }
}

function resetCustom() {
  customIds.value = []
  search.value = ''
}

onMounted(async () => {
  try {
    all.value = await getPlayersCompare()
  } catch (e) {
    error.value = t('compare.loadError')
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="mx-auto max-w-6xl px-4 py-8">
    <header class="mb-8">
      <h1 class="text-4xl font-extrabold text-white">{{ t('compare.title') }}</h1>
      <p class="mt-2 text-base text-white/80">{{ t('compare.subtitle') }}</p>
    </header>

    <div v-if="loading" class="py-20 text-center text-slate-400">{{ t('compare.loading') }}</div>
    <div v-else-if="error" class="py-20 text-center text-red-500">{{ error }}</div>

    <template v-else>
      <!-- 自定义自选：搜索 + 已选 -->
      <div class="mb-6 rounded-xl bg-white p-4 shadow-sm">
        <div class="mb-3 flex items-center gap-2">
          <input
            v-model="search"
            :placeholder="t('compare.searchPlaceholder')"
            class="w-full rounded-lg border border-slate-200 bg-slate-100 px-3 py-2 text-sm text-black placeholder-black/50 outline-none focus:border-indigo-400"
          />
        </div>
        <div v-if="available.length" class="mb-3">
          <div class="mb-2 text-sm font-medium text-black/70">{{ t('compare.hotPlayers') }}</div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="p in available"
              :key="p.id"
              @click="toggleCustom(p)"
              :disabled="customIds.length >= 4 && !customIds.includes(p.id)"
              :class="[
                'rounded-full px-3 py-1 text-sm transition',
                customIds.includes(p.id)
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-100 text-slate-800 hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-50',
              ]"
            >
              {{ nameOf(p) }}
            </button>
          </div>
        </div>
        <div v-if="isCustom" class="flex flex-wrap gap-2">
          <span class="text-xs text-black/50">{{ t('compare.selected') }}</span>
          <span
            v-for="id in customIds"
            :key="id"
            class="inline-flex items-center gap-1 rounded-full bg-indigo-100 px-2.5 py-0.5 text-xs text-black"
          >
            {{ nameOf(playerById(id)) }}
            <button @click="toggleCustom(playerById(id))" class="text-black/60 hover:text-black">×</button>
          </span>
        </div>
      </div>

      <!-- 雷达对比 -->
      <div class="rounded-2xl bg-white p-4 shadow-sm sm:p-6">
        <div v-if="radarPlayers.length === 0" class="flex h-[420px] flex-col items-center justify-center text-black/60">
          <span class="mb-2 text-2xl">🎯</span>
          <p class="text-lg font-medium">{{ t('compare.emptyTitle') }}</p>
          <p class="text-sm">{{ t('compare.emptyHint') }}</p>
        </div>
        <RadarCompare v-else :players="radarPlayers" />
      </div>
    </template>
  </div>
</template>
