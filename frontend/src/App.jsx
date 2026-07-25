import { useState, useRef } from 'react'

const EXAMPLES = [
  'What is the waiting period for pre-existing diseases?',
  'How do I use cashless hospitalisation?',
  'Is there a limit on room rent?',
  'Is maternity covered?',
]

const CORPUS = { insurers: 9, clauses: 1831 }

const THEMES = {
  light: {
    bg: '#F1EEE8', panel: '#FFFFFF', panelSunk: '#F7F5F0', ink: '#1A1917',
    inkSoft: '#6B665D', line: '#E5E1D8', accent: '#1D6E63', accentSoft: '#E3EFEC',
    accentInk: '#12463F', chip: '#EDEAE3', amber: '#B5751A', amberSoft: '#F7EEDD',
    shadow: '0 1px 2px rgba(26,25,23,.04), 0 8px 24px rgba(26,25,23,.06)',
  },
  dark: {
    bg: '#17161A', panel: '#201F24', panelSunk: '#1A191E', ink: '#EDEBE6',
    inkSoft: '#9B968C', line: '#2E2C33', accent: '#3FB8A6', accentSoft: '#1D3230',
    accentInk: '#8FE0D2', chip: '#2A2830', amber: '#D9A54B', amberSoft: '#2C2519',
    shadow: '0 1px 2px rgba(0,0,0,.3), 0 12px 32px rgba(0,0,0,.35)',
  },
}

export default function App() {
  const [mode, setMode] = useState('light')
  const [query, setQuery] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [active, setActive] = useState(null)
  const cardRefs = useRef({})
  const t = THEMES[mode]

  async function run(q) {
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
    setTimeout(() => setActive((a) => (a === n ? null : a)), 2000)
  }

  function renderAnswer(text) {
    const parts = text.split(/(\[[\d,\s]+\])/g)
    return parts.map((part, i) => {
      const m = part.match(/^\[([\d,\s]+)\]$/)
      if (!m) return <span key={i}>{part}</span>
      const nums = m[1].split(',').map((s) => parseInt(s.trim(), 10)).filter(Boolean)
      return (
        <span key={i}>
          {nums.map((n) => (
            <button key={n} onClick={() => jumpTo(n)} style={{
              margin: '0 2px', height: 20, minWidth: 20, padding: '0 6px',
              borderRadius: 6, border: 'none', cursor: 'pointer',
              background: t.accentSoft, color: t.accentInk,
              fontSize: 12, fontWeight: 600, fontFamily: 'inherit',
              verticalAlign: 'baseline', transition: 'all .15s',
            }}>{n}</button>
          ))}
        </span>
      )
    })
  }

  const font = "'Inter', -apple-system, system-ui, sans-serif"

  return (
    <div style={{
      minHeight: '100vh', background: t.bg, color: t.ink, fontFamily: font,
      transition: 'background .3s, color .3s',
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap');
        * { box-sizing: border-box; }
        body { margin: 0; }
        button:focus-visible { outline: 2px solid ${t.accent}; outline-offset: 2px; }
        @keyframes pulse { 0%,100%{opacity:.5} 50%{opacity:.85} }
        @keyframes fadeUp { from{opacity:0; transform:translateY(8px)} to{opacity:1; transform:translateY(0)} }
        ::placeholder { color: ${t.inkSoft}; opacity: .7; }
        @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
      `}</style>

      <div style={{ maxWidth: 1120, margin: '0 auto', padding: '28px 32px 80px' }}>

        {/* Top bar */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 40, flexWrap: 'wrap', gap: 12 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 11 }}>
            <div style={{
              width: 34, height: 34, borderRadius: 10, background: t.accent,
              display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
            }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M12 3l7 4v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V7l7-4z" stroke="#fff" strokeWidth="1.8" strokeLinejoin="round"/>
                <path d="M9 12l2 2 4-4" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <div>
              <div style={{ fontSize: 19, fontWeight: 700, letterSpacing: '-.02em', lineHeight: 1 }}>Evidex</div>
              <div style={{ fontSize: 11.5, color: t.inkSoft, marginTop: 2, letterSpacing: '.01em' }}>Insurance policy intelligence</div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 7, padding: '7px 13px',
              background: t.panel, borderRadius: 999, fontSize: 12.5, color: t.inkSoft, boxShadow: t.shadow,
            }}>
              <span style={{ width: 6, height: 6, borderRadius: 99, background: t.accent, display: 'inline-block' }} />
              {CORPUS.insurers} insurers · {CORPUS.clauses.toLocaleString()} clauses indexed
            </div>
            <button onClick={() => setMode(mode === 'light' ? 'dark' : 'light')} aria-label="Toggle theme" style={{
              width: 38, height: 38, borderRadius: 999, border: 'none', cursor: 'pointer',
              background: t.panel, color: t.ink, boxShadow: t.shadow,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {mode === 'light'
                ? <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><path d="M21 12.8A9 9 0 1111.2 3a7 7 0 009.8 9.8z" stroke={t.ink} strokeWidth="1.8" strokeLinejoin="round"/></svg>
                : <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="4.5" stroke={t.ink} strokeWidth="1.8"/><path d="M12 2v2M12 20v2M4 12H2M22 12h-2M5 5l1.5 1.5M17.5 17.5L19 19M19 5l-1.5 1.5M6.5 17.5L5 19" stroke={t.ink} strokeWidth="1.8" strokeLinecap="round"/></svg>}
            </button>
          </div>
        </div>

        {/* Hero */}
        <div style={{ maxWidth: 720, margin: '0 auto 28px', textAlign: 'center' }}>
          <h1 style={{
            fontFamily: "'Newsreader', serif", fontSize: 40, lineHeight: 1.12,
            fontWeight: 500, letterSpacing: '-.01em', margin: '8px 0 12px',
          }}>
            Ask your policies.<br /><span style={{ fontStyle: 'italic', color: t.accent }}>Verify every word.</span>
          </h1>
          <p style={{ fontSize: 15, color: t.inkSoft, lineHeight: 1.5, margin: '0 auto', maxWidth: 480 }}>
            Every answer is drawn only from the indexed policy documents and cites the exact clause, insurer, and page it came from.
          </p>
        </div>

        {/* Search */}
        <div style={{
          maxWidth: 720, margin: '0 auto', background: t.panel, borderRadius: 18,
          padding: 8, boxShadow: t.shadow, display: 'flex', gap: 8, alignItems: 'center',
        }}>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && run()}
            placeholder="Ask about coverage, waiting periods, exclusions…"
            style={{
              flex: 1, border: 'none', background: 'transparent', outline: 'none',
              fontSize: 15, color: t.ink, padding: '12px 14px', fontFamily: font,
            }}
          />
          <button onClick={() => run()} disabled={loading || query.trim().length < 3} style={{
            padding: '12px 22px', borderRadius: 12, border: 'none',
            background: query.trim().length < 3 ? t.chip : t.accent,
            color: query.trim().length < 3 ? t.inkSoft : '#fff',
            fontSize: 14, fontWeight: 600, cursor: query.trim().length < 3 ? 'default' : 'pointer',
            fontFamily: font, transition: 'all .2s', flexShrink: 0,
          }}>
            {loading ? 'Searching…' : 'Ask'}
          </button>
        </div>

        {/* Examples */}
        {!data && !loading && !error && (
          <div style={{ maxWidth: 720, margin: '16px auto 0', display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
            {EXAMPLES.map((e) => (
              <button key={e} onClick={() => run(e)} style={{
                padding: '8px 14px', borderRadius: 999, border: `1px solid ${t.line}`,
                background: 'transparent', color: t.inkSoft, fontSize: 12.5, cursor: 'pointer',
                fontFamily: font, transition: 'all .15s',
              }}
                onMouseEnter={(ev) => { ev.currentTarget.style.color = t.ink; ev.currentTarget.style.borderColor = t.accent }}
                onMouseLeave={(ev) => { ev.currentTarget.style.color = t.inkSoft; ev.currentTarget.style.borderColor = t.line }}
              >{e}</button>
            ))}
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{
            maxWidth: 720, margin: '24px auto 0', background: t.amberSoft,
            borderRadius: 14, padding: '16px 20px', fontSize: 13.5, color: t.amber,
            boxShadow: t.shadow,
          }}>
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div style={{ maxWidth: 860, margin: '32px auto 0' }}>
            <div style={{ background: t.panel, borderRadius: 18, padding: 24, boxShadow: t.shadow }}>
              {[80, 100, 65].map((w, i) => (
                <div key={i} style={{ height: 14, width: `${w}%`, borderRadius: 7, background: t.chip, marginBottom: 12, animation: 'pulse 1.4s ease-in-out infinite' }} />
              ))}
            </div>
          </div>
        )}

        {/* Results */}
        {data && (
          <div style={{ maxWidth: 860, margin: '32px auto 0', animation: 'fadeUp .4s ease' }}>

            {/* Answer / refusal card */}
            <div style={{
              background: data.found ? t.panel : t.amberSoft, borderRadius: 20,
              padding: '26px 28px', boxShadow: t.shadow,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
                <span style={{ fontSize: 11, fontWeight: 600, letterSpacing: '.08em', textTransform: 'uppercase', color: data.found ? t.accent : t.amber }}>
                  {data.found ? 'Answer' : 'No matching clause'}
                </span>
                <span style={{ flex: 1, height: 1, background: t.line }} />
              </div>
              <p style={{ fontSize: 16.5, lineHeight: 1.62, margin: 0, letterSpacing: '-.005em' }}>
                {data.found ? renderAnswer(data.answer) : data.answer}
              </p>
              {data.sources.length > 0 && (
                <div style={{
                  display: 'flex', flexWrap: 'wrap', gap: 16, marginTop: 20, paddingTop: 16,
                  borderTop: `1px solid ${t.line}`, fontSize: 12, color: t.inkSoft,
                }}>
                  <Meta label="Response" value={`${data.elapsed_ms} ms`} t={t} />
                  <Meta label="Model" value={data.provider} t={t} />
                  <Meta label="Retrieved" value={`${data.sources.length} clauses`} t={t} />
                  <Meta label="Cited" value={`${data.sources.filter(s => s.cited).length} sources`} t={t} accent />
                  {data.invalid_citations.length > 0 && (
                    <Meta label="Invalid" value={data.invalid_citations.join(', ')} t={t} />
                  )}
                </div>
              )}
            </div>

            {/* Sources */}
            {data.sources.length > 0 && (
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, margin: '32px 4px 14px' }}>
                  <span style={{ fontSize: 12.5, fontWeight: 600, letterSpacing: '.04em', textTransform: 'uppercase', color: t.inkSoft }}>Sources</span>
                  <span style={{ fontSize: 12, color: t.inkSoft, opacity: .7 }}>click a citation above to trace it</span>
                  <span style={{ flex: 1, height: 1, background: t.line }} />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {data.sources.map((s) => {
                    const isActive = active === s.index
                    const promoted = s.vector_rank > 5
                    return (
                      <div key={s.index} ref={(el) => (cardRefs.current[s.index] = el)} style={{
                        background: t.panel, borderRadius: 16, padding: '18px 20px',
                        boxShadow: t.shadow, transition: 'all .3s',
                        border: `1.5px solid ${isActive ? t.accent : 'transparent'}`,
                        transform: isActive ? 'scale(1.008)' : 'scale(1)',
                      }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 14 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
                            <span style={{
                              width: 24, height: 24, borderRadius: 7, flexShrink: 0,
                              background: s.cited ? t.accent : t.chip,
                              color: s.cited ? '#fff' : t.inkSoft,
                              display: 'flex', alignItems: 'center', justifyContent: 'center',
                              fontSize: 12.5, fontWeight: 700,
                            }}>{s.index}</span>
                            <div style={{ minWidth: 0 }}>
                              <div style={{ fontSize: 14, fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{s.insurer}</div>
                              <div style={{ fontSize: 12, color: t.inkSoft, marginTop: 1 }}>Page {s.page}</div>
                            </div>
                          </div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
                            {s.cited && (
                              <span style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: '.03em', padding: '3px 8px', borderRadius: 6, background: t.accentSoft, color: t.accentInk }}>CITED</span>
                            )}
                            <RelevanceBar score={s.rerank_score} t={t} />
                          </div>
                        </div>
                        <p style={{ fontSize: 13.5, lineHeight: 1.6, color: t.inkSoft, margin: '13px 0 0' }}>{s.text}</p>
                        {promoted && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 12 }}>
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M12 19V5M5 12l7-7 7 7" stroke={t.accent} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                            <span style={{ fontSize: 11.5, color: t.accent, fontWeight: 500 }}>Promoted by reranker — vector search ranked this #{s.vector_rank}</span>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function Meta({ label, value, t, accent }) {
  return (
    <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <span style={{ opacity: .75 }}>{label}</span>
      <span style={{ fontWeight: 600, color: accent ? t.accent : t.ink }}>{value}</span>
    </span>
  )
}

function RelevanceBar({ score, t }) {
  const filled = Math.max(1, Math.min(6, Math.round((score / 11) * 6)))
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <div style={{ display: 'flex', gap: 2.5 }}>
        {Array.from({ length: 6 }).map((_, i) => (
          <span key={i} style={{ width: 4, height: 13, borderRadius: 2, background: i < filled ? t.accent : t.chip }} />
        ))}
      </div>
      <span style={{ fontSize: 11, color: t.inkSoft, fontVariantNumeric: 'tabular-nums', minWidth: 26 }}>{score.toFixed(1)}</span>
    </div>
  )
}