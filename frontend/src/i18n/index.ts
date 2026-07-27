import { createI18n } from 'vue-i18n'

const messages = {
  zh: {
    brand: 'JackeyFootball',
    ageUnit: '岁',
    power: { allRank: '全部球员综合实力排名' },
    nav: { home: '首页', power: '综合实力', data: '各数据', compare: '球员对比' },
    hero: {
      title: 'JackeyFootball为你展现出最完整的球员数据',
    },
    pos: { all: '全部', forward: '前锋', midfielder: '中场', defender: '后卫', goalkeeper: '门将' },
    common: { loading: '数据加载中…', empty: '暂无球员数据。', captain: '队长', vice: '副队长', loadError: '加载数据失败' },
    sideNav: {
      powerDesc: '全部球员综合实力排名',
      dataDesc: '进球 / 助攻 / 传球逐项排名',
      compareDesc: '全体 / 跨位置雷达图对比',
    },
    detail: {
      score: '综合实力评分',
      stats: '基础数据',
      breakdown: '评分维度分解',
      honors: '团队荣誉',
      awards: '个人荣誉',
      none: '暂无记录',
      close: '关闭',
    },
    data: { title: '各数据排名', subtitle: '全部球员按所选指标统一排名对比。', loading: '加载中…', loadError: '加载数据失败' },
    compare: { title: '球员对比 · 综合数据', subtitle: '搜索并选择球员进行对比，最多支持 4 人。', searchPlaceholder: '搜索球员以加入对比（最多 4 人）…', hotPlayers: '热门球员：', selected: '已选：', emptyTitle: '暂无球员对比', emptyHint: '请在上方搜索并选择最多 4 名球员进行雷达图对比。', loading: '加载中…', loadError: '加载球员数据失败', clear: '清空' },
    stats: {
      season: '赛季', appearances: '出场', minutes_played: '分钟', goals: '进球', assists: '助攻',
      shots_total: '射门', shots_on_target: '射正', pass_accuracy: '传球成功率', key_passes: '关键传球',
      tackles: '抢断', interceptions: '拦截', clearances: '解围', blocks: '封堵', saves: '扑救',
      clean_sheets: '零封', goals_conceded: '失球', dribbles_completed: '成功过人', aerial_duels_won: '空中对抗',
    },
    bd: {
      stats_raw: '个人数据', award_raw: '个人荣誉', honor_raw: '团队荣誉', market_value_raw: '身价', leadership_raw: '队长影响力',
    },
    dataMetrics: {
      goals: '进球', assists: '助攻', appearances: '出场', minutes_played: '分钟',
      shots_total: '射门', shots_on_target: '射正', pass_accuracy: '传球成功率', key_passes: '关键传球',
      tackles: '抢断', interceptions: '拦截', clearances: '解围', blocks: '封堵',
      saves: '扑救', clean_sheets: '零封', goals_conceded: '失球', dribbles_completed: '过人', aerial_duels_won: '争顶成功',
    },
    footer: {
      disclaimer: '数据来源参考：StatsBomb / FBref / TheSportsDB 等公开数据，仅供学习研究，非商业用途。',
    },
    scoring: {
      title: '评分怎么算的？',
      formula: '综合实力 = 同位置归一化后加权',
      statsWeight: '个人数据能力 50%',
      awardWeight: '个人荣誉 25%',
      honorWeight: '团队荣誉 20%',
      marketWeight: '身价 3%',
      leaderWeight: '领导力 2%',
      tip: '所有分值按同位置统一归一化到 0-100 区间。',
    },
  },
  en: {
    brand: 'JackeyFootball',
    ageUnit: 'y',
    power: { allRank: 'All Players Power Ranking' },
    nav: { home: 'Home', power: 'Power', data: 'Stats', compare: 'Compare' },
    hero: {
      title: 'JackeyFootball reveals the most complete player data for you',
    },
    pos: { all: 'All', forward: 'Forward', midfielder: 'Midfield', defender: 'Defender', goalkeeper: 'Goalkeeper' },
    common: { loading: 'Loading…', empty: 'No player data yet.', captain: 'Captain', vice: 'Vice', loadError: 'Failed to load data' },
    sideNav: {
      powerDesc: 'All Players Power Ranking',
      dataDesc: 'Goals / Assists / Passes by metric',
      compareDesc: 'Cross-position Radar Comparison',
    },
    detail: {
      score: 'Overall Rating',
      stats: 'Key Stats',
      breakdown: 'Rating Breakdown',
      honors: 'Team Honors',
      awards: 'Individual Awards',
      none: 'None',
      close: 'Close',
    },
    data: { title: 'Data Ranking', subtitle: 'All players ranked by selected metric.', loading: 'Loading…', loadError: 'Failed to load data' },
    compare: { title: 'Player Compare', subtitle: 'Search and select up to 4 players for comparison.', searchPlaceholder: 'Search players to compare (max 4)…', hotPlayers: 'Hot Players: ', selected: 'Selected: ', emptyTitle: 'No players selected', emptyHint: 'Search and select up to 4 players above for radar comparison.', loading: 'Loading…', loadError: 'Failed to load players', clear: 'Clear' },
    stats: {
      season: 'Season', appearances: 'Apps', minutes_played: 'Mins', goals: 'Goals', assists: 'Assists',
      shots_total: 'Shots', shots_on_target: 'On Target', pass_accuracy: 'Pass Acc.', key_passes: 'Key Passes',
      tackles: 'Tackles', interceptions: 'Interceptions', clearances: 'Clearances', blocks: 'Blocks', saves: 'Saves',
      clean_sheets: 'Clean Sheets', goals_conceded: 'GA', dribbles_completed: 'Dribbles', aerial_duels_won: 'Aerial Duels',
    },
    bd: {
      stats_raw: 'Stats', award_raw: 'Individual Awards', honor_raw: 'Team Honors', market_value_raw: 'Market Value', leadership_raw: 'Leadership',
    },
    dataMetrics: {
      goals: 'Goals', assists: 'Assists', appearances: 'Apps', minutes_played: 'Mins',
      shots_total: 'Shots', shots_on_target: 'On Target', pass_accuracy: 'Pass Acc.', key_passes: 'Key Passes',
      tackles: 'Tackles', interceptions: 'Interceptions', clearances: 'Clearances', blocks: 'Blocks',
      saves: 'Saves', clean_sheets: 'Clean Sheets', goals_conceded: 'GA', dribbles_completed: 'Dribbles', aerial_duels_won: 'Aerial Duels',
    },
    footer: {
      disclaimer: 'Data sources: StatsBomb / FBref / TheSportsDB and other public datasets. For educational & research purposes only. Non-commercial use.',
    },
    scoring: {
      title: 'How is the rating calculated?',
      formula: 'Overall = Normalized (within position) Weighted Score',
      statsWeight: 'Statistical Performance 50%',
      awardWeight: 'Individual Awards 25%',
      honorWeight: 'Team Honors 20%',
      marketWeight: 'Market Value 3%',
      leaderWeight: 'Leadership 2%',
      tip: 'All scores are normalized within the same position to a 0-100 scale.',
    },
  },
}

const saved = (typeof localStorage !== 'undefined' && localStorage.getItem('jf_lang')) || 'zh'

const i18n = createI18n({
  legacy: false,
  locale: saved,
  fallbackLocale: 'zh',
  messages,
})

export default i18n
