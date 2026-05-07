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

export interface TranslateResponse {
  text: string
}

export async function detectIdioms(text: string): Promise<DetectResponse> {
  const res = await axios.post<DetectResponse>('/api/detect', { text })
  return res.data
}

export async function translateText(text: string): Promise<TranslateResponse> {
  const res = await axios.post<TranslateResponse>('/api/translate', {
    text,
    to: 'en',
  })
  return res.data
}
