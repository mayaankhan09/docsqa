import { useState, useRef } from 'react'

const EXAMPLES = [
  'What is the waiting period for pre-existing diseases?',
  'How do I use the cashless hospitalisation facility?',
  'Is there a limit on room rent?',
  'Is maternity covered?',
]

export default function App() {
  const [query, setQuery] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [active, setActive] = useState(null)
  const cardRefs = useRef({})

  async function ask(q) {
    const text = (q ?? query).trim()
    if (text.length < 3) return

    setQuery(text)
    setLoading(true)
    setError(null)
    setData(null)
    setActive(null)

    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text }),
      })
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}))
        throw new Error(detail.detail || `Request failed (${res.status})`)
      }
      setData(await res.json())
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  function jumpTo(n) {
    setActive(n)
    cardRefs.current[n]?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  // Split answer text on [n] or [n, m] markers and render chips
  function renderAnswer(text) {
    const parts = text.split(/(\[[\d,\s]+\])/g)
    return parts.map((part, i) => {
      const m = part.match(/^\[([\d,\s]+)\]$/)
      if (!m) return <span key={i}>{part}</span>
      const nums = m[1].split(',').map((s) => parseInt(s.trim(), 10)).filter(Boolean)
      return (
        <span key={i}>
          {nums.map((n) => (
            <button
              key={n}
              onClick={() => jumpTo(n)}
              className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded
                         bg-slate-200 px-1.5 text-xs font-medium text-slate-700
                         hover:bg-slate-300 transition"
            >
              {n}
            </button>
          ))}
        </span>
      )
    })
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="mx-auto max-w-3xl px-6 py-12">

        <header className="mb-8">
          <h1 className="text-3xl font-semibold tracking-tight">DocsQA</h1>
          <p className="mt-1 text-slate-600">
            Ask about health insurance policy terms. Every answer cites the clause it came from.
          </p>
          <p className="mt-2 text-xs text-slate-500">
            Indexed: 9 policy documents from 9 Indian insurers (IRDAI public filings)
          </p>
        </header>

        <div className="flex gap-2">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && ask()}
            placeholder="e.g. What is the waiting period for pre-existing diseases?"
            className="flex-1 rounded-lg border border-slate-300 bg-white px-4 py-2.5
                       text-sm outline-none focus:border-slate-500"
          />
          <button
            onClick={() => ask()}
            disabled={loading || query.trim().length < 3}
            className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white
                       hover:bg-slate-700 disabled:opacity-40 transition"
          >
            {loading ? 'Searching…' : 'Ask'}
          </button>
        </div>

        {!data && !loading && (
          <div className="mt-4 flex flex-wrap gap-2">
            {EXAMPLES.map((e) => (
              <button
                key={e}
                onClick={() => ask(e)}
                className="rounded-full border border-slate-300 px-3 py-1 text-xs
                           text-slate-600 hover:border-slate-500 hover:text-slate-900 transition"
              >
                {e}
              </button>
            ))}
          </div>
        )}

        {error && (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
            {error}
          </div>
        )}

        {loading && (
          <div className="mt-8 space-y-3">
            <div className="h-4 w-3/4 animate-pulse rounded bg-slate-200" />
            <div className="h-4 w-full animate-pulse rounded bg-slate-200" />
            <div className="h-4 w-2/3 animate-pulse rounded bg-slate-200" />
          </div>
        )}

        {data && (
          <div className="mt-8">
            <div className={`rounded-xl border p-5 ${
              data.found ? 'border-slate-200 bg-white' : 'border-amber-200 bg-amber-50'
            }`}>
              <p className="leading-relaxed">{renderAnswer(data.answer)}</p>
              <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 border-t border-slate-100 pt-3
                              text-xs text-slate-500">
                <span>{data.elapsed_ms} ms</span>
                <span>{data.provider}</span>
                <span>{data.sources.length} retrieved</span>
                {data.invalid_citations.length > 0 && (
                  <span className="font-medium text-red-600">
                    invalid citations: {data.invalid_citations.join(', ')}
                  </span>
                )}
              </div>
            </div>

            {data.sources.length > 0 && (
              <>
                <h2 className="mt-8 mb-3 text-sm font-medium text-slate-500">Sources</h2>
                <div className="space-y-3">
                  {data.sources.map((s) => (
                    <div
                      key={s.index}
                      ref={(el) => (cardRefs.current[s.index] = el)}
                      className={`rounded-lg border bg-white p-4 transition ${
                        active === s.index
                          ? 'border-slate-900 ring-2 ring-slate-900/10'
                          : 'border-slate-200'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-2">
                          <span className="flex h-5 min-w-5 items-center justify-center rounded
                                           bg-slate-900 px-1.5 text-xs font-medium text-white">
                            {s.index}
                          </span>
                          <span className="text-sm font-medium">{s.citation}</span>
                          {s.cited && (
                            <span className="rounded bg-emerald-50 px-1.5 py-0.5 text-[10px]
                                             font-medium text-emerald-700">
                              cited
                            </span>
                          )}
                        </div>
                        <span className="shrink-0 text-xs text-slate-400">
                          {s.rerank_score.toFixed(2)} · was #{s.vector_rank}
                        </span>
                      </div>
                      <p className="mt-2 text-sm leading-relaxed text-slate-600">{s.text}</p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}