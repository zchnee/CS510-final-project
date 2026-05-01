import type { IdiomMatch } from '../api/client'

interface Props {
  match: IdiomMatch
  isActive: boolean
  onClick: () => void
}

export default function IdiomCard({ match, isActive, onClick }: Props) {
  return (
    <div
      onClick={onClick}
      className={`border rounded-xl p-4 cursor-pointer transition-all ${
        isActive
          ? 'border-purple-400 bg-purple-50 shadow-md'
          : 'border-gray-200 bg-white hover:border-purple-300 hover:shadow-sm'
      }`}
    >
      {/* Idiom + primary meaning */}
      <div className="flex items-baseline gap-3 flex-wrap">
        <span className="text-2xl font-bold font-chinese text-purple-700">
          {match.idiom}
        </span>
        <span className="text-gray-700 font-medium">{match.meaning_en}</span>
      </div>

      {/* Alternative meanings */}
      {match.alternative_meanings_en.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {match.alternative_meanings_en.map((alt, i) => (
            <span
              key={i}
              className="text-xs bg-gray-100 text-gray-600 rounded-full px-2 py-0.5"
            >
              {alt}
            </span>
          ))}
        </div>
      )}

      {/* Example sentence */}
      {match.sentence_zh && (
        <div className="mt-3 border-t border-gray-100 pt-3 space-y-1">
          <p className="text-sm text-gray-800 font-chinese">{match.sentence_zh}</p>
          {match.sentence_en && (
            <p className="text-sm text-gray-500 italic">{match.sentence_en}</p>
          )}
        </div>
      )}
    </div>
  )
}
