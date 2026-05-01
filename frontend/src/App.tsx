import { useState } from 'react'
import './App.css'
import { detectIdioms, type IdiomMatch } from './api/client'
import InputPanel from './components/InputPanel'
import IdiomHighlighter from './components/IdiomHighlighter'
import IdiomCard from './components/IdiomCard'
import TranslationOutput from './components/TranslationOutput'

function App() {
  const [text, setText] = useState('')
  const [idioms, setIdioms] = useState<IdiomMatch[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hasSearched, setHasSearched] = useState(false)
  const [activeIdiom, setActiveIdiom] = useState<string | null>(null)

  async function handleDetect() {
    setLoading(true)
    setError(null)
    try {
      const result = await detectIdioms(text)
      setIdioms(result.idioms)
      setHasSearched(true)
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message)
      } else {
        setError('Failed to reach backend. Make sure the server is running.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-purple-900">
          🀄 Chinese Idiom Translator
        </h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Detect and explain Chinese idioms (成语) in any text
        </p>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        {/* Input */}
        <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
            Input
          </h2>
          <InputPanel
            value={text}
            onChange={setText}
            onSubmit={handleDetect}
            loading={loading}
          />
        </section>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm">
            {error}
          </div>
        )}

        {/* Translation output (placeholder until Andrew's API is integrated) */}
        {hasSearched && (
          <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-3">
              Translation
            </h2>
            <TranslationOutput />
          </section>
        )}

        {/* Highlighted input + idiom cards */}
        {hasSearched && (
          <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-4">
            <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
              Idioms Detected
            </h2>

            {/* Annotated text */}
            <div className="bg-gray-50 rounded-xl p-4">
              <IdiomHighlighter
                text={text}
                idioms={idioms}
                activeIdiom={activeIdiom}
                onHover={setActiveIdiom}
              />
            </div>

            {/* Cards */}
            {idioms.length === 0 ? (
              <p className="text-gray-400 text-sm">No idioms found in this text.</p>
            ) : (
              <div className="space-y-3">
                {idioms.map((match) => (
                  <IdiomCard
                    key={match.idiom + match.start}
                    match={match}
                    isActive={activeIdiom === match.idiom}
                    onClick={() =>
                      setActiveIdiom(activeIdiom === match.idiom ? null : match.idiom)
                    }
                  />
                ))}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  )
}

export default App
