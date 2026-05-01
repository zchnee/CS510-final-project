interface Props {
  placeholder?: string
}

export default function TranslationOutput({ placeholder = 'Translation will appear here once the translation API is integrated.' }: Props) {
  return (
    <div className="w-full min-h-[80px] p-3 border border-dashed border-gray-300 rounded-lg bg-gray-50 text-gray-400 text-sm italic">
      {placeholder}
    </div>
  )
}
