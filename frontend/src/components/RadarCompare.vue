<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { RadarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import type { PlayerDetail } from '@/types'
import { useI18n } from 'vue-i18n'

use([RadarChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const { t, locale } = useI18n()

const props = defineProps<{ players: PlayerDetail[] }>()

function nameOf(p: PlayerDetail) {
  return locale.value === 'en' ? p.name_en || p.name : p.name
}

const PALETTE = ['#FF5A36', '#1FB6C9', '#2ECC71', '#9B59F6', '#FFC53D', '#FF7AB6']

const option = computed(() => {
  const rawDims = Object.keys(props.players[0]?.score_breakdown ?? {})
  const dims = rawDims.filter((d) => d !== 'age_raw' && d !== 'team_strength_raw')
  const indicator = dims.map((d) => ({ name: t('bd.' + d), max: 100 }))
  return {
    color: PALETTE,
    tooltip: {},
    legend: {
      data: props.players.map((p) => nameOf(p)),
      textStyle: { color: '#000000' },
      top: 0,
    },
    radar: {
      backgroundColor: '#000000',
      indicator,
      radius: '62%',
      axisName: { color: '#000000' },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,.15)' } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: 'rgba(0,0,0,.2)' } },
    },
    series: [
      {
        type: 'radar',
        data: props.players.map((p) => ({
          name: nameOf(p),
          value: dims.map((d) => p.score_breakdown?.[d] ?? 0),
          lineStyle: { width: 2 },
          areaStyle: { opacity: 0.12 },
        })),
      },
    ],
  }
})
</script>

<template>
  <VChart v-if="players.length" :option="option" autoresize class="w-full h-[420px]" />
  <div v-else class="text-muted text-center py-10">{{ $t('compare.empty') }}</div>
</template>
