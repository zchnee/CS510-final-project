import type { IdiomMatch } from '../api/client'

interface Props {
  text: string
  idioms: IdiomMatch[]
  activeIdiom: string | null
  onHover: (idiom: string | null) => void
}

export default function IdiomHighlighter({ text, idioms, activeIdiom, onHover }: Props) {
  if (!idioms.length) {
    return <p className="text-lg leading-relaxed font-chinese">{text}</p>
  }

  // Build a sorted list of non-overlapping spans
  const sorted = [...idioms].sort((a, b) => a.start - b.start)
  const parts: React.ReactNode[] = []
  let cursor = 0

  for (const match of sorted) {
    if (match.start > cursor) {
      parts.push(
        <span key={`plain-${cursor}`}>{text.slice(cursor, match.start)}</span>
      )
    }
    const isActive = activeIdiom === match.idiom
    parts.push(
      <mark
        key={`idiom-${match.start}`}
        className={`cursor-pointer rounded px-0.5 transition-colors ${
          isActive
            ? 'bg-purple-300 text-purple-900'
            : 'bg-yellow-200 text-yellow-900 hover:bg-yellow-300'
        }`}
        onMouseEnter={() => onHover(match.idiom)}
        onMouseLeave={() => onHover(null)}
      >
        {match.idiom}
      </mark>
    )
    cursor = match.end
  }

  if (cursor < text.length) {
    parts.push(<span key={`plain-end`}>{text.slice(cursor)}</span>)
  }

  return <p className="text-lg leading-relaxed font-chinese">{parts}</p>
}
