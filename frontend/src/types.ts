export type Position = 'forward' | 'midfielder' | 'defender' | 'goalkeeper'

export interface PlayerStats {
  season: string
  appearances: number
  minutes_played: number
  goals: number
  assists: number
  shots_total: number
  shots_on_target: number
  pass_accuracy: number
  key_passes: number
  tackles: number
  interceptions: number
  clearances: number
  blocks: number
  saves: number
  clean_sheets: number
  goals_conceded: number
  dribbles_completed: number
  aerial_duels_won: number
  [key: string]: string | number
}

export interface PlayerListItem {
  id: number
  name: string
  name_en: string
  position: Position
  nationality: string
  age: number
  market_value_euro: number
  current_club: string
  club_league: string
  is_captain: boolean
  is_vice_captain: boolean
  national_team: string
  club_strength_score: number
  national_team_strength_score: number
  image_url: string
  overall_score: number
}

export interface PlayerDetail extends PlayerListItem {
  stats: PlayerStats | null
  honors: Array<{ honor_name: string; competition_name: string; count: number; year?: string }>
  awards: Array<{ award_name: string; count: number; year?: string }>
  score_breakdown: Record<string, number> | null
}

export interface PlayerWithStats extends PlayerListItem {
  stats: PlayerStats | null
}

export const POSITION_META: Record<Position, { zh: string; en: string; color: string }> = {
  forward: { zh: '前锋', en: 'Forward', color: '#FF5A36' },
  midfielder: { zh: '中场', en: 'Midfielder', color: '#1FB6C9' },
  defender: { zh: '后卫', en: 'Defender', color: '#2ECC71' },
  goalkeeper: { zh: '门将', en: 'Goalkeeper', color: '#9B59F6' },
}
