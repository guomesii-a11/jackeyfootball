export const CLUB_ZH_MAP: Record<string, string> = {
  'Manchester City': '曼彻斯特城',
  'Real Madrid': '皇家马德里',
  'Paris Saint-Germain': '巴黎圣日耳曼',
  'Paris SG': '巴黎圣日耳曼',
  'FC Barcelona': '巴塞罗那',
  'Liverpool': '利物浦',
  'Bayern Munich': '拜仁慕尼黑',
  'Inter Milan': '国际米兰',
  'Arsenal': '阿森纳',
  'Bayer Leverkusen': '勒沃库森',
  'Chelsea': '切尔西',
  'Atletico Madrid': '马德里竞技',
  'Borussia Dortmund': '多特蒙德',
  'Tottenham': '托特纳姆热刺',
  'Aston Villa': '阿斯顿维拉',
  'Newcastle': '纽卡斯尔联',
  'Napoli': '那不勒斯',
  'AC Milan': 'AC米兰',
  'Juventus': '尤文图斯',
  'RB Leipzig': '莱比锡红牛',
  'Stuttgart': '斯图加特',
  'Wrexham': '雷克瑟姆',
  'Al-Hilal': '利雅得新月',
  'Chicago Fire': '芝加哥火焰队',
  'Neom': '新未来城体育',
  'Galatasaray': '加拉塔萨雷',
  'Fenerbahçe': '费内巴切',
}

export function clubNameOf(en: string, locale: string): string {
  if (locale === 'en') return en
  return CLUB_ZH_MAP[en] || en
}

export const NATION_ZH_MAP: Record<string, string> = {
  'France': '法国',
  'Spain': '西班牙',
  'Portugal': '葡萄牙',
  'Germany': '德国',
  'England': '英格兰',
  'Brazil': '巴西',
  'Argentina': '阿根廷',
  'Italy': '意大利',
  'Netherlands': '荷兰',
  'Belgium': '比利时',
  'Croatia': '克罗地亚',
  'Poland': '波兰',
  'Norway': '挪威',
  'Uruguay': '乌拉圭',
  'Denmark': '丹麦',
  'Sweden': '瑞典',
  'Switzerland': '瑞士',
  'Senegal': '塞内加尔',
  'Ghana': '加纳',
  'Nigeria': '尼日利亚',
  'Cameroon': '喀麦隆',
  'Morocco': '摩洛哥',
  'Egypt': '埃及',
  'South Korea': '韩国',
  'Japan': '日本',
  'USA': '美国',
  'Wales': '威尔士',
  'Scotland': '苏格兰',
  'Turkey': '土耳其',
  'Saudi Arabia': '沙特阿拉伯',
  'Slovenia': '斯洛文尼亚',
}

export function nationalityOf(en: string, locale: string): string {
  if (!en) return ''
  if (locale === 'en') return en
  return NATION_ZH_MAP[en] || en
}

export const HONOR_ZH_MAP: Record<string, string> = {
  '世界杯冠军': 'World Cup Winner',
  '世界杯亚军': 'World Cup Runner-up',
  '世界杯季军': 'World Cup 3rd Place',
  '欧洲杯冠军': 'UEFA EURO Winner',
  '欧洲杯四强': 'UEFA EURO Semifinalist',
  '欧国联冠军': 'UEFA Nations League Winner',
  '欧国联亚军': 'UEFA Nations League Runner-up',
  '欧冠冠军': 'UEFA Champions League Winner',
  '世俱杯冠军': 'FIFA Club World Cup Winner',
  '英超冠军': 'Premier League Winner',
  '西甲冠军': 'La Liga Winner',
  '德甲冠军': 'Bundesliga Winner',
  '意甲冠军': 'Serie A Winner',
  '法甲冠军': 'Ligue 1 Winner',
  '足总杯冠军': 'FA Cup Winner',
  '美洲杯冠军': 'Copa América Winner',
}

export function honorNameOf(zh: string, locale: string): string {
  if (!zh) return ''
  if (locale === 'zh') return zh
  return HONOR_ZH_MAP[zh] || zh
}

export const AWARD_ZH_MAP: Record<string, string> = {
  '金球奖': 'Ballon d\'Or',
  '国际足联最佳球员': 'FIFA The Best Player',
  '欧足联最佳球员': 'UEFA Player of the Year',
  '世界杯金球奖': 'World Cup Golden Ball',
  '欧洲金靴': 'European Golden Shoe',
  '法甲金靴': 'Ligue 1 Golden Boot',
  '英超金靴': 'Premier League Golden Boot',
  '德甲金靴': 'Bundesliga Top Scorer',
  '意甲金靴': 'Serie A Top Scorer',
  '科帕奖': 'Kopa Trophy',
  '赛季最佳阵容': 'Team of the Season',
  '雅辛奖': 'Yashin Trophy',
  'FIFA最佳门将': 'FIFA Best Goalkeeper',
  '联赛金手套': 'League Golden Glove',
  'PFA年度最佳球员': 'PFA Player of the Year',
}

export function awardNameOf(zh: string, locale: string): string {
  if (!zh) return ''
  if (locale === 'zh') return zh
  return AWARD_ZH_MAP[zh] || zh
}
