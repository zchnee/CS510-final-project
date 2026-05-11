interface Props {
  value: string
  onChange: (val: string) => void
  onSubmit: () => void
  loading: boolean
}

export default function InputPanel({ value, onChange, onSubmit, loading }: Props) {
  return (
    <div className="flex flex-col gap-3">
      <textarea
        className="w-full h-40 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-purple-400 text-lg font-chinese"
        placeholder="输入中文文本… (Enter Chinese text)"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) onSubmit()
        }}
      />
      <button
        onClick={onSubmit}
        disabled={loading || !value.trim()}
        className="self-end px-6 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer transition-colors"
      >
        {loading ? 'Detecting…' : 'Detect Idioms'}
      </button>
    </div>
  )
}
