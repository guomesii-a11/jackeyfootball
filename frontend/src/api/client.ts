import axios from 'axios'
import type { PlayerListItem, PlayerDetail, PlayerWithStats } from '@/types'

const http = axios.create({ baseURL: '/api' })

export async function getPlayers(position?: string): Promise<PlayerListItem[]> {
  const { data } = await http.get<PlayerListItem[]>('/players', {
    params: position && position !== 'all' ? { position } : {},
  })
  return data
}

export async function getPlayersWithStats(): Promise<PlayerWithStats[]> {
  const { data } = await http.get<PlayerWithStats[]>('/players/stats')
  return data
}

export async function getPlayer(id: number): Promise<PlayerDetail> {
  const { data } = await http.get<PlayerDetail>(`/players/${id}`)
  return data
}

export async function getPlayersCompare(): Promise<PlayerDetail[]> {
  const { data } = await http.get<PlayerDetail[]>('/players/compare')
  return data
}

export default http
