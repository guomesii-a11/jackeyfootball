<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { getPlayers } from '@/api/client'
import { POSITION_META, type PlayerListItem, type PlayerDetail, type Position } from '@/types'
import { clubNameOf, nationalityOf, honorNameOf, awardNameOf } from '@/constants'

const { t, locale } = useI18n()

const players = ref<PlayerListItem[]>([])
const loading = ref(true)
const errored = ref<Set<number>>(new Set())
const detail = ref<PlayerDetail | null>(null)
const drawerOpen = ref(false)

// 位置筛选
const selectedPos = ref<string>('all')
const POS_FILTERS = [
  { key: 'all', label: 'pos.all' },
  { key: 'forward', label: 'pos.forward' },
  { key: 'midfielder', label: 'pos.midfielder' },
  { key: 'defender', label: 'pos.defender' },
  { key: 'goalkeeper', label: 'pos.goalkeeper' },
]

const filtered = computed(() => {
  if (selectedPos.value === 'all') return [...players.value]
  return players.value.filter(p => p.position === selectedPos.value)
})

const ranked = computed(() =>
  filtered.value.sort((a, b) => b.overall_score - a.overall_score),
)

function nameOf(p: PlayerListItem) {
  return locale.value === 'zh' ? p.name : p.name_en || p.name
}
function marketValue(v: number) {
  if (!v) return ''
  return '€' + (v >= 1e6 ? (v / 1e6).toFixed(1) + 'M' : Math.round(v / 1e3) + 'K')
}
function initials(name: string) {
  if (/^[A-Za-z\s.]+$/.test(name)) {
    return name.split(/\s+/).map((w) => w[0]).join('').slice(0, 2).toUpperCase()
  }
  return name.slice(0, 2)
}
function onImgError(id: number) {
  errored.value.add(id)
  errored.value = new Set(errored.value)
}
async function openDetail(id: number) {
  const { data } = await axios.get<PlayerDetail>(`/api/players/${id}`)
  detail.value = data
  drawerOpen.value = true
}
function closeDrawer() {
  drawerOpen.value = false
}

const STAT_LABELS: Record<string, Record<string, string>> = {
  zh: { season:'赛季',appearances:'出场',minutes_played:'分钟',goals:'进球',assists:'助攻',
    shots_total:'射门',shots_on_target:'射正',pass_accuracy:'传球成功率',key_passes:'关键传球',
    tackles:'抢断',interceptions:'拦截',clearances:'解围',blocks:'封堵',saves:'扑救',
    clean_sheets:'零封',goals_conceded:'失球',dribbles_completed:'成功过人',aerial_duels_won:'空中对抗',
  },
  en: { season:'Season',appearances:'Apps',minutes_played:'Mins',goals:'Goals',assists:'Assists',
    shots_total:'Shots',shots_on_target:'On Target',pass_accuracy:'Pass Acc.',key_passes:'Key Passes',
    tackles:'Tackles',interceptions:'Interceptions',clearances:'Clearances',blocks:'Blocks',saves:'Saves',
    clean_sheets:'Clean Sheets',goals_conceded:'GA',dribbles_completed:'Dribbles',aerial_duels_won:'Aerial Duels',
  },
}
const BD_LABELS: Record<string, Record<string, string>> = {
  zh: { stats_raw:'个人数据',award_raw:'个人荣誉',honor_raw:'团队荣誉',market_value_raw:'身价',leadership_raw:'队长影响力' },
  en: { stats_raw:'Stats',award_raw:'Individual Awards',honor_raw:'Team Honors',market_value_raw:'Market Value',leadership_raw:'Leadership' },
}

onMounted(async () => {
  try {
    players.value = await getPlayers()
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <!-- 全体统一排名 -->
    <div v-if="loading" class="text-center text-muted py-20">{{ t('common.loading') }}</div>
    <div v-else-if="!players.length" class="text-center text-muted py-20">{{ t('common.empty') }}</div>

    <template v-else>
      <!-- 位置筛选标签 -->
      <div class="flex flex-wrap gap-2 mb-5">
        <button
          v-for="pos in POS_FILTERS"
          :key="pos.key"
          class="px-4 py-1.5 rounded-full text-sm font-semibold transition-all duration-200 border"
          :class="selectedPos === pos.key
            ? 'bg-white text-black border-white'
            : 'bg-white/5 text-muted border-white/10 hover:bg-white/15 hover:text-ink'"
          @click="selectedPos = pos.key"
        >
          {{ t(pos.label) }}
        </button>
      </div>

      <section class="mb-8">
        <div class="flex items-center gap-2 mb-3 text-lg font-bold">
          <span class="w-3 h-3 rounded-full" style="background:#FFC53D; box-shadow:0 0 12px #FFC53D"></span>
          {{ t('power.allRank') }}
          <span class="text-muted font-normal text-sm">({{ ranked.length }})</span>
        </div>

        <div
          v-for="(p, i) in ranked"
          :key="p.id"
          class="grid grid-cols-[44px_52px_1fr_72px] md:grid-cols-[54px_52px_1fr_160px_64px] items-center gap-4 glass-soft rounded-2xl px-4 py-3 mb-3 cursor-pointer transition-all duration-200 hover:-translate-y-0.5 hover:border-white/30"
          @click="openDetail(p.id)"
        >
          <div class="text-center font-extrabold text-xl tabular-nums" :class="i < 3 ? 'text-gold' : 'text-muted'">{{ i + 1 }}</div>

          <img v-if="p.image_url && !errored.has(p.id)" :src="p.image_url" :alt="p.name" class="w-[52px] h-[52px] rounded-full object-cover border-2 border-white/25" loading="lazy" @error="onImgError(p.id)" />
          <div v-else class="w-[52px] h-[52px] rounded-full flex items-center justify-center font-extrabold text-lg text-bg0" :style="{ background: POSITION_META[p.position].color }">{{ initials(p.name) }}</div>

          <div class="min-w-0">
            <div class="font-bold truncate">
              {{ nameOf(p) }}
              <span v-if="p.is_captain" class="ml-2 text-xs font-extrabold text-gold border border-gold rounded px-1.5 align-middle">{{ t('common.captain') }}</span>
              <span v-else-if="p.is_vice_captain" class="ml-2 text-xs font-extrabold text-gold border border-gold rounded px-1.5 align-middle">{{ t('common.vice') }}</span>
            </div>
            <div class="text-sm text-muted truncate">{{ clubNameOf(p.current_club, locale) }} · {{ p.age }}{{ t('ageUnit') }}</div>
          </div>

          <div class="hidden md:block text-right text-sm text-muted">{{ nationalityOf(p.nationality, locale) }}<br />{{ marketValue(p.market_value_euro) }}</div>

          <div class="text-right">
            <div class="font-extrabold text-2xl tabular-nums" :style="{ color: POSITION_META[p.position].color }">{{ p.overall_score.toFixed(1) }}</div>
            <div class="h-2 rounded-full bg-white/10 mt-1 overflow-hidden">
              <div class="h-full rounded-full" :style="{ width: p.overall_score + '%', background: `linear-gradient(90deg, ${POSITION_META[p.position].color}, #FFC53D)` }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- 评分说明卡 -->
      <section class="glass-soft rounded-2xl p-5 text-sm">
        <div class="font-bold text-base mb-3 flex items-center gap-2">
          <span class="text-gold">?</span>
          {{ t('scoring.title') }}
        </div>
        <div class="text-muted mb-3">{{ t('scoring.formula') }}：</div>
        <div class="space-y-2 mb-3">
          <div class="flex justify-between items-center">
            <span>{{ t('scoring.statsWeight') }}</span>
            <span class="font-bold text-ink">50%</span>
          </div>
          <div class="h-1.5 rounded-full bg-white/10 overflow-hidden">
            <div class="h-full rounded-full" style="width:50%;background:#1FB6C9"></div>
          </div>
          <div class="flex justify-between items-center">
            <span>{{ t('scoring.awardWeight') }}</span>
            <span class="font-bold text-ink">25%</span>
          </div>
          <div class="h-1.5 rounded-full bg-white/10 overflow-hidden">
            <div class="h-full rounded-full" style="width:25%;background:#9B59F6"></div>
          </div>
          <div class="flex justify-between items-center">
            <span>{{ t('scoring.honorWeight') }}</span>
            <span class="font-bold text-ink">20%</span>
          </div>
          <div class="h-1.5 rounded-full bg-white/10 overflow-hidden">
            <div class="h-full rounded-full" style="width:20%;background:#FFC53D"></div>
          </div>
          <div class="flex justify-between items-center">
            <span>{{ t('scoring.marketWeight') }}</span>
            <span class="font-bold text-ink">3%</span>
          </div>
          <div class="flex justify-between items-center">
            <span>{{ t('scoring.leaderWeight') }}</span>
            <span class="font-bold text-ink">2%</span>
          </div>
        </div>
        <div class="text-xs text-muted opacity-75">{{ t('scoring.tip') }}</div>
      </section>
    </template>

    <!-- 详情抽屉 -->
    <div v-if="drawerOpen" class="fixed inset-0 z-40 bg-black/50" @click="closeDrawer"></div>
    <aside
      v-if="detail"
      class="fixed top-0 right-0 h-full w-[min(440px,92vw)] z-50 glass rounded-l-2xl p-6 overflow-y-auto transition-transform duration-300"
      :class="drawerOpen ? 'translate-x-0' : 'translate-x-full'"
    >
      <button class="absolute top-4 right-4 w-9 h-9 rounded-full bg-white/10 border border-white/15 text-ink hover:bg-white/20" @click="closeDrawer">✕</button>

      <div class="flex items-center gap-4 mt-2">
        <img v-if="detail.image_url" :src="detail.image_url" class="w-16 h-16 rounded-full object-cover border-2 border-white/25" />
        <div v-else class="w-16 h-16 rounded-full flex items-center justify-center font-extrabold text-xl text-bg0" :style="{ background: POSITION_META[detail.position].color }">{{ initials(detail.name) }}</div>
        <div>
          <div class="text-2xl font-extrabold">{{ nameOf(detail) }}</div>
          <div class="text-sm text-muted">{{ POSITION_META[detail.position][locale] }} · {{ clubNameOf(detail.current_club, locale) }} · {{ nationalityOf(detail.national_team, locale) }}</div>
        </div>
      </div>

      <div class="my-4 p-4 rounded-2xl bg-white/5 text-center">
        <div class="text-4xl font-extrabold text-gold">{{ detail.overall_score.toFixed(1) }}</div>
        <div class="text-sm text-muted">{{ t('detail.score') }}</div>
      </div>

      <div class="section-title">{{ t('detail.stats') }}</div>
      <div class="grid grid-cols-2 gap-2">
        <div v-for="(v, k) in (detail.stats || {})" :key="k" v-show="k !== 'id' && k !== 'player_id' && v != null && v !== ''" class="bg-white/5 border border-white/10 rounded-xl p-2.5">
          <div class="text-xs text-muted">{{ STAT_LABELS[locale]?.[k] || k }}</div>
          <div class="text-lg font-bold">{{ k === 'pass_accuracy' ? v + '%' : v }}</div>
        </div>
        <div v-if="!detail.stats" class="col-span-2 text-muted text-sm py-2">{{ t('detail.none') }}</div>
      </div>

      <div class="section-title">{{ t('detail.breakdown') }}</div>
      <div v-for="(v, k) in (detail.score_breakdown || {})" :key="k" class="mb-2">
        <div class="flex justify-between text-sm mb-1"><span>{{ BD_LABELS[locale]?.[k] || k }}</span><span>{{ v }}</span></div>
        <div class="h-2 rounded-full bg-white/10 overflow-hidden">
          <div class="h-full rounded-full" :style="{ width: v + '%', background: 'linear-gradient(90deg,#1FB6C9,#FFC53D)' }"></div>
        </div>
      </div>

      <div class="section-title">{{ t('detail.honors') }}</div>
      <div>
        <span v-for="(h, i) in detail.honors" :key="'h' + i" class="inline-block text-xs font-semibold bg-white/5 border border-white/10 rounded-lg px-2.5 py-1 mr-1.5 mt-1">{{ honorNameOf(h.honor_name, locale) }} ×{{ h.count }}{{ h.year ? ' · ' + h.year : '' }}</span>
        <span v-if="!detail.honors.length" class="text-muted text-sm">{{ t('detail.none') }}</span>
      </div>

      <div class="section-title">{{ t('detail.awards') }}</div>
      <div>
        <span v-for="(a, i) in detail.awards" :key="'a' + i" class="inline-block text-xs font-semibold bg-white/5 border border-white/10 rounded-lg px-2.5 py-1 mr-1.5 mt-1">{{ awardNameOf(a.award_name, locale) }} ×{{ a.count }}{{ a.year ? ' · ' + a.year : '' }}</span>
        <span v-if="!detail.awards.length" class="text-muted text-sm">{{ t('detail.none') }}</span>
      </div>
    </aside>
  </div>
</template>

<style scoped>
.section-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-1);
  margin: 20px 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
</style>
