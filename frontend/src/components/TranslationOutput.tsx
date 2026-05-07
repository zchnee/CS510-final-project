interface Props {
  text?: string
}

export default function TranslationOutput({ text }: Props) {
  return (
    <div className="w-full min-h-[80px] p-3 border border-gray-200 rounded-lg bg-gray-50 text-gray-700 text-sm whitespace-pre-wrap">
      {text || 'Translation will appear here.'}
    </div>
  )
}
