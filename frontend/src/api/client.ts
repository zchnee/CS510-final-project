import axios from 'axios'

export interface IdiomMatch {
  idiom: string
  start: number
  end: number
  meaning_en: string
  alternative_meanings_en: string[]
  sentence_zh: string
  sentence_en: string
}

export interface DetectResponse {
  idioms: IdiomMatch[]
}

export async function detectIdioms(text: string): Promise<DetectResponse> {
  const res = await axios.post<DetectResponse>('/api/detect', { text })
  return res.data
}
