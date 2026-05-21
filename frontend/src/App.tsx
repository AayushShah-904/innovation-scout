import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Search, ChevronRight, Sparkles, Database, Globe, FileText,
  CheckCircle2, XCircle, BarChart3, Shield, ArrowRight,
  Loader2, AlertTriangle, RotateCcw, Zap, BookOpen,
  TrendingUp, FlaskConical, ExternalLink, Activity,
  CircleDot, Download, Copy, Check
} from 'lucide-react'

// Use VITE_API_URL in production (Render backend URL), fallback to '/api' for local dev proxy
const API_BASE = import.meta.env.VITE_API_URL ?? '/api'

type Stage = 'search' | 'scanning' | 'review' | 'report'

interface RankedResult {
  title: string
  url: string
  source: string
  reason: string
  relevance_score: number
  credibility_score: number
}

interface SearchData {
  session_id: string
  status: string
  keywords: string[]
  ranked_results: RankedResult[]
}

const SCAN_STEPS = [
  { icon: Zap,         label: 'Parsing query with Gemini 2.5 Flash',           detail: 'Extracting semantic keywords & intents' },
  { icon: BookOpen,    label: 'Scanning arXiv scientific repository',           detail: 'Querying academic papers & preprints' },
  { icon: Database,    label: 'Searching local pgvector knowledge base',        detail: 'Running cosine similarity embeddings' },
  { icon: Globe,       label: 'Grounding live web intelligence via Gemini',     detail: 'Retrieving real-time market signals' },
  { icon: BarChart3,   label: 'AI Ranker scoring relevance & credibility',      detail: 'Evaluating each asset on 0.0–1.0 scales' },
  { icon: Shield,      label: 'HITL checkpoint — awaiting human review',        detail: 'LangGraph state machine paused for you' },
]

const SUGGESTED_QUERIES = [
  'Eco-friendly bio-plastics for protective phone cases',
  'Quantum computing error correction techniques 2024',
  'CRISPR gene editing applications in agriculture',
  'Next-gen solid-state battery materials for EVs',
]

// ─── Score Bar ───────────────────────────────────────────────────────────────

function ScoreBar({ value, color }: { value: number; color: string }) {
  const [width, setWidth] = useState(0)
  useEffect(() => {
    const t = setTimeout(() => setWidth(value * 100), 120)
    return () => clearTimeout(t)
  }, [value])

  return (
    <div className="score-bar-track">
      <div
        className="score-bar-fill"
        style={{ width: `${width}%`, background: color }}
      />
    </div>
  )
}

// ─── Source Badge ─────────────────────────────────────────────────────────────

function SourceBadge({ source }: { source: string }) {
  const cfg: Record<string, { color: string; icon: React.ElementType; bg: string }> = {
    ARXIV:  { color: '#f87171', bg: 'rgba(239,68,68,0.12)',   icon: BookOpen },
    DB:     { color: '#34d399', bg: 'rgba(52,211,153,0.12)',  icon: Database },
    WEB:    { color: '#60a5fa', bg: 'rgba(96,165,250,0.12)',  icon: Globe    },
    VECTOR: { color: '#34d399', bg: 'rgba(52,211,153,0.12)',  icon: Database },
  }
  const key = source.toUpperCase().replace('ARXIV', 'ARXIV')
  const c = cfg[key] || cfg.WEB
  const Icon = c.icon
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold font-mono"
      style={{ color: c.color, background: c.bg, border: `1px solid ${c.color}30` }}
    >
      <Icon size={11} />
      {source.toUpperCase()}
    </span>
  )
}

// ─── Discovery Card ───────────────────────────────────────────────────────────

function DiscoveryCard({ item, index }: { item: RankedResult; index: number }) {
  const [expanded, setExpanded] = useState(false)
  const rel = parseFloat(item.relevance_score as unknown as string) || 0
  const crd = parseFloat(item.credibility_score as unknown as string) || 0

  const relColor = rel >= 0.75 ? '#34d399' : rel >= 0.5 ? '#fbbf24' : '#f87171'
  const crdColor = crd >= 0.75 ? '#60a5fa' : crd >= 0.5 ? '#a78bfa' : '#f87171'

  return (
    <div
      className="glass-card glass-card-hover p-5 animate-fade-in"
      style={{ animationDelay: `${index * 80}ms`, animationFillMode: 'both' }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <div
            className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold"
            style={{ background: 'rgba(124,77,255,0.15)', color: '#9474ff', border: '1px solid rgba(124,77,255,0.25)' }}
          >
            {index + 1}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-sm leading-snug mb-1" style={{ color: '#e8e6f8' }}>
              {item.title || 'Untitled Discovery'}
            </h3>
            <SourceBadge source={item.source || 'WEB'} />
          </div>
        </div>
        <a
          href={item.url || '#'}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 p-1.5 rounded-lg transition-all hover:bg-white/5"
          style={{ color: '#6b6898' }}
          title="Open source"
        >
          <ExternalLink size={15} />
        </a>
      </div>

      {/* Score Meters */}
      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs" style={{ color: '#6b6898' }}>Relevance</span>
            <span className="text-xs font-mono font-semibold" style={{ color: relColor }}>
              {(rel * 100).toFixed(0)}%
            </span>
          </div>
          <ScoreBar value={rel} color={relColor} />
        </div>
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs" style={{ color: '#6b6898' }}>Credibility</span>
            <span className="text-xs font-mono font-semibold" style={{ color: crdColor }}>
              {(crd * 100).toFixed(0)}%
            </span>
          </div>
          <ScoreBar value={crd} color={crdColor} />
        </div>
      </div>

      {/* Reasoning Toggle */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs transition-colors w-full text-left"
        style={{ color: expanded ? '#9474ff' : '#6b6898' }}
      >
        <ChevronRight
          size={13}
          style={{ transform: expanded ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }}
        />
        {expanded ? 'Hide AI reasoning' : 'View AI engineering rationale'}
      </button>

      {expanded && (
        <div
          className="mt-2.5 p-3 rounded-xl text-xs leading-relaxed animate-fade-in"
          style={{ background: 'rgba(124,77,255,0.06)', border: '1px solid rgba(124,77,255,0.12)', color: '#c4c2e0' }}
        >
          {item.reason || 'No reasoning text profile populated.'}
        </div>
      )}
    </div>
  )
}

// ─── Sidebar ──────────────────────────────────────────────────────────────────

function Sidebar({ stage }: { stage: Stage }) {
  const navItems = [
    { id: 'search',   icon: Search,      label: 'Query Input'    },
    { id: 'scanning', icon: Activity,    label: 'Agent Scan'     },
    { id: 'review',   icon: Shield,      label: 'HITL Review'    },
    { id: 'report',   icon: FileText,    label: 'R&D Briefing'   },
  ]
  const stageOrder = ['search', 'scanning', 'review', 'report']
  const currentIdx = stageOrder.indexOf(stage)

  return (
    <aside
      className="hidden lg:flex flex-col w-64 flex-shrink-0 h-screen sticky top-0 overflow-y-auto"
      style={{ background: 'rgba(13,11,30,0.95)', borderRight: '1px solid rgba(124,77,255,0.12)' }}
    >
      {/* Logo */}
      <div className="p-6 pb-4">
        <div className="flex items-center gap-3 mb-1">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center animate-pulse-glow"
            style={{ background: 'linear-gradient(135deg, #7c4dff, #5a17e3)' }}
          >
            <FlaskConical size={18} className="text-white" />
          </div>
          <div>
            <div className="font-bold text-sm" style={{ color: '#e8e6f8' }}>Innovation Scout</div>
            <div className="text-xs" style={{ color: '#6b6898' }}>R&D Intelligence</div>
          </div>
        </div>
        <div
          className="mt-3 px-3 py-1.5 rounded-lg text-xs font-mono"
          style={{ background: 'rgba(52,211,153,0.08)', color: '#34d399', border: '1px solid rgba(52,211,153,0.2)' }}
        >
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 mr-2 animate-pulse" />
          Backend Connected
        </div>
      </div>

      {/* Pipeline Steps */}
      <div className="px-4 pb-4">
        <div className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: '#2e2a5c' }}>
          Pipeline
        </div>
        <nav className="space-y-1">
          {navItems.map((item, idx) => {
            const Icon = item.icon
            const isActive = item.id === stage
            const isDone = idx < currentIdx
            return (
              <div
                key={item.id}
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all"
                style={{
                  background: isActive ? 'rgba(124,77,255,0.15)' : 'transparent',
                  color: isActive ? '#b8a5ff' : isDone ? '#34d399' : '#6b6898',
                  border: isActive ? '1px solid rgba(124,77,255,0.3)' : '1px solid transparent',
                }}
              >
                {isDone ? (
                  <CheckCircle2 size={16} style={{ color: '#34d399', flexShrink: 0 }} />
                ) : (
                  <Icon size={16} style={{ flexShrink: 0 }} />
                )}
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <div
                    className="ml-auto w-1.5 h-1.5 rounded-full"
                    style={{ background: '#7c4dff' }}
                  />
                )}
              </div>
            )
          })}
        </nav>
      </div>

      <div className="mt-auto px-4 pb-6">
        <div
          className="p-3 rounded-xl text-xs space-y-1"
          style={{ background: 'rgba(18,16,42,0.8)', border: '1px solid rgba(124,77,255,0.12)' }}
        >
          <div className="font-semibold mb-2" style={{ color: '#c4c2e0' }}>Stack</div>
          {[['LangGraph', 'State Machine'], ['Gemini 2.5 Flash', 'LLM Backbone'], ['pgvector', 'Vector DB'], ['arXiv API', 'Scientific DB']].map(([name, desc]) => (
            <div key={name} className="flex items-center justify-between">
              <span style={{ color: '#6b6898' }}>{name}</span>
              <span style={{ color: '#9474ff' }}>{desc}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  )
}

// ─── Search Stage ─────────────────────────────────────────────────────────────

function SearchStage({
  onSearch
}: {
  onSearch: (query: string) => void
}) {
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = () => {
    if (query.trim()) onSearch(query.trim())
  }

  const handleKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleSubmit()
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-16 animate-fade-in">
      {/* Hero */}
      <div className="text-center mb-12">
        <div
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold mb-6"
          style={{ background: 'rgba(124,77,255,0.12)', color: '#b8a5ff', border: '1px solid rgba(124,77,255,0.25)' }}
        >
          <Sparkles size={12} />
          Multi-Agent Knowledge Retrieval Engine
        </div>
        <h1 className="text-4xl font-extrabold leading-tight mb-4 gradient-text">
          Innovation Scout
        </h1>
        <p className="text-lg" style={{ color: '#6b6898' }}>
          3-way parallel agent scans across arXiv, vector DB, and live web — with AI-powered scoring
          and a Human-in-the-Loop verification gate.
        </p>
      </div>

      {/* Agent Source Badges */}
      <div className="flex flex-wrap justify-center gap-3 mb-10">
        {[
          { icon: BookOpen, label: 'arXiv Papers', color: '#f87171', bg: 'rgba(239,68,68,0.08)' },
          { icon: Database, label: 'pgvector DB',  color: '#34d399', bg: 'rgba(52,211,153,0.08)' },
          { icon: Globe,    label: 'Live Web',     color: '#60a5fa', bg: 'rgba(96,165,250,0.08)' },
        ].map(({ icon: Icon, label, color, bg }) => (
          <div
            key={label}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold"
            style={{ background: bg, color, border: `1px solid ${color}25` }}
          >
            <Icon size={13} />
            {label}
          </div>
        ))}
      </div>

      {/* Search Input Card */}
      <div className="glass-card p-6 mb-6">
        <label className="block text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: '#6b6898' }}>
          Research Query
        </label>
        <textarea
          ref={inputRef}
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Describe your research problem or technology domain…"
          rows={3}
          className="w-full resize-none text-sm leading-relaxed outline-none placeholder:opacity-50 bg-transparent"
          style={{ color: '#e8e6f8', fontFamily: 'var(--font-sans)' }}
          id="research-query-input"
        />
        <div className="flex items-center justify-between mt-4 pt-4" style={{ borderTop: '1px solid rgba(124,77,255,0.12)' }}>
          <span className="text-xs" style={{ color: '#6b6898' }}>
            ⌘ Enter to search • Ctrl+Enter on Windows
          </span>
          <button
            id="search-submit-btn"
            onClick={handleSubmit}
            disabled={!query.trim()}
            className="btn-primary"
          >
            <Search size={16} />
            Launch Scan
            <ArrowRight size={14} />
          </button>
        </div>
      </div>

      {/* Suggested Queries */}
      <div>
        <div className="text-xs font-semibold uppercase tracking-widest mb-3 text-center" style={{ color: '#6b6898' }}>
          Suggested Research Queries
        </div>
        <div className="grid sm:grid-cols-2 gap-3">
          {SUGGESTED_QUERIES.map((q, i) => (
            <button
              key={i}
              onClick={() => setQuery(q)}
              className="text-left p-3.5 rounded-xl text-sm transition-all"
              style={{
                background: 'rgba(18,16,42,0.6)',
                border: '1px solid rgba(124,77,255,0.12)',
                color: '#c4c2e0',
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLElement).style.borderColor = 'rgba(124,77,255,0.35)'
                ;(e.currentTarget as HTMLElement).style.color = '#e8e6f8'
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLElement).style.borderColor = 'rgba(124,77,255,0.12)'
                ;(e.currentTarget as HTMLElement).style.color = '#c4c2e0'
              }}
            >
              <TrendingUp size={12} className="inline mr-2 opacity-50" />
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

// ─── Scanning Stage ───────────────────────────────────────────────────────────

function ScanningStage({ query }: { query: string }) {
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep(prev => (prev < SCAN_STEPS.length - 1 ? prev + 1 : prev))
    }, 1800)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="max-w-2xl mx-auto px-6 py-16 animate-fade-in">
      {/* Spinner + Title */}
      <div className="text-center mb-10">
        <div className="relative inline-flex items-center justify-center mb-6">
          <div
            className="w-20 h-20 rounded-full animate-spin-slow"
            style={{ border: '2px solid rgba(124,77,255,0.15)', borderTopColor: '#7c4dff' }}
          />
          <div
            className="absolute w-12 h-12 rounded-full flex items-center justify-center"
            style={{ background: 'linear-gradient(135deg, #7c4dff22, #5a17e322)', border: '1px solid rgba(124,77,255,0.3)' }}
          >
            <Activity size={20} style={{ color: '#7c4dff' }} />
          </div>
        </div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: '#e8e6f8' }}>
          Agents Running
        </h2>
        <p className="text-sm" style={{ color: '#6b6898' }}>
          Processing: <span className="font-medium" style={{ color: '#b8a5ff' }}>"{query}"</span>
        </p>
      </div>

      {/* Step List */}
      <div className="glass-card p-6 space-y-3">
        {SCAN_STEPS.map((step, idx) => {
          const Icon = step.icon
          const isActive = idx === activeStep
          const isDone = idx < activeStep

          return (
            <div
              key={idx}
              className="flex items-start gap-4 p-3 rounded-xl transition-all"
              style={{
                background: isActive ? 'rgba(124,77,255,0.08)' : 'transparent',
                border: isActive ? '1px solid rgba(124,77,255,0.2)' : '1px solid transparent',
                opacity: idx > activeStep ? 0.35 : 1,
              }}
            >
              <div
                className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
                style={{
                  background: isDone
                    ? 'rgba(52,211,153,0.15)'
                    : isActive
                    ? 'rgba(124,77,255,0.2)'
                    : 'rgba(255,255,255,0.04)',
                  border: isDone
                    ? '1px solid rgba(52,211,153,0.3)'
                    : isActive
                    ? '1px solid rgba(124,77,255,0.4)'
                    : '1px solid rgba(255,255,255,0.06)',
                }}
              >
                {isDone ? (
                  <CheckCircle2 size={16} style={{ color: '#34d399' }} />
                ) : isActive ? (
                  <Loader2 size={16} style={{ color: '#9474ff' }} className="animate-spin" />
                ) : (
                  <Icon size={16} style={{ color: '#6b6898' }} />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div
                  className="text-sm font-medium"
                  style={{ color: isDone ? '#34d399' : isActive ? '#e8e6f8' : '#6b6898' }}
                >
                  {step.label}
                </div>
                {isActive && (
                  <div className="text-xs mt-0.5 animate-fade-in" style={{ color: '#9474ff' }}>
                    {step.detail}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      <p className="text-center text-xs mt-6" style={{ color: '#6b6898' }}>
        This may take 30–90 seconds depending on web sources…
      </p>
    </div>
  )
}

// ─── Review Stage ─────────────────────────────────────────────────────────────

function ReviewStage({
  data,
  onApprove,
  onReject,
  isApproving,
}: {
  data: SearchData
  onApprove: () => void
  onReject: () => void
  isApproving: boolean
}) {
  const keywords = data.keywords || []
  const results  = data.ranked_results || []

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <div
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold mb-4"
          style={{ background: 'rgba(251,191,36,0.1)', color: '#fbbf24', border: '1px solid rgba(251,191,36,0.25)' }}
        >
          <CircleDot size={11} className="animate-pulse" />
          LangGraph Paused — Human Review Required
        </div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: '#e8e6f8' }}>
          Review Research Discoveries
        </h2>
        <p className="text-sm" style={{ color: '#6b6898' }}>
          The AI pipeline has paused execution. Evaluate {results.length} ranked discovery assets before authorizing report compilation.
        </p>
      </div>

      {/* Keywords */}
      {keywords.length > 0 && (
        <div className="glass-card p-5 mb-6">
          <div className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: '#6b6898' }}>
            Agent Parsing Targets
          </div>
          <div className="flex flex-wrap gap-2">
            {keywords.map((kw, i) => (
              <span
                key={i}
                className="px-3 py-1.5 rounded-lg text-xs font-mono font-medium"
                style={{ background: 'rgba(124,77,255,0.1)', color: '#b8a5ff', border: '1px solid rgba(124,77,255,0.2)' }}
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Results Summary Bar */}
      <div
        className="grid grid-cols-3 gap-4 mb-6 p-4 rounded-2xl"
        style={{ background: 'rgba(18,16,42,0.6)', border: '1px solid rgba(124,77,255,0.1)' }}
      >
        {[
          { label: 'Total Discoveries', value: results.length, color: '#b8a5ff', icon: Sparkles },
          { label: 'Avg Relevance',  value: results.length ? `${(results.reduce((s, r) => s + (parseFloat(r.relevance_score as unknown as string) || 0), 0) / results.length * 100).toFixed(0)}%` : '—', color: '#34d399', icon: TrendingUp },
          { label: 'Avg Credibility', value: results.length ? `${(results.reduce((s, r) => s + (parseFloat(r.credibility_score as unknown as string) || 0), 0) / results.length * 100).toFixed(0)}%` : '—', color: '#60a5fa', icon: Shield },
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} className="text-center">
            <div className="flex justify-center mb-1">
              <Icon size={16} style={{ color }} />
            </div>
            <div className="text-xl font-bold" style={{ color }}>{value}</div>
            <div className="text-xs mt-0.5" style={{ color: '#6b6898' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Discovery Cards Grid */}
      {results.length === 0 ? (
        <div
          className="glass-card p-10 text-center"
        >
          <AlertTriangle size={32} className="mx-auto mb-3" style={{ color: '#fbbf24' }} />
          <p style={{ color: '#c4c2e0' }}>No matching documents found across standard sources.</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          {results.map((item, idx) => (
            <DiscoveryCard key={idx} item={item} index={idx} />
          ))}
        </div>
      )}

      {/* Action Buttons */}
      <div
        className="flex flex-col sm:flex-row gap-4 p-5 rounded-2xl sticky bottom-6"
        style={{ background: 'rgba(6,5,15,0.92)', backdropFilter: 'blur(20px)', border: '1px solid rgba(124,77,255,0.2)' }}
      >
        <div className="flex-1">
          <div className="text-xs font-semibold mb-0.5" style={{ color: '#c4c2e0' }}>Human Decision Gate</div>
          <div className="text-xs" style={{ color: '#6b6898' }}>Your approval resumes the LangGraph state machine</div>
        </div>
        <div className="flex gap-3">
          <button
            id="reject-btn"
            onClick={onReject}
            className="btn-danger"
            disabled={isApproving}
          >
            <XCircle size={16} />
            Reject & Reset
          </button>
          <button
            id="approve-btn"
            onClick={onApprove}
            className="btn-primary"
            disabled={isApproving}
          >
            {isApproving ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Compiling…
              </>
            ) : (
              <>
                <CheckCircle2 size={16} />
                Approve & Compile
                <ArrowRight size={14} />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── Report Stage ─────────────────────────────────────────────────────────────

function ReportStage({ report, onNewSession }: { report: string; onNewSession: () => void }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(report)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = 'innovation-scout-briefing.md'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <div
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold mb-4"
          style={{ background: 'rgba(52,211,153,0.1)', color: '#34d399', border: '1px solid rgba(52,211,153,0.25)' }}
        >
          <CheckCircle2 size={11} />
          R&D Synthesis Complete
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold" style={{ color: '#e8e6f8' }}>
              Intelligence Briefing
            </h2>
            <p className="text-sm mt-1" style={{ color: '#6b6898' }}>
              AI-synthesized report with verified sources and credibility scores
            </p>
          </div>
          <div className="flex gap-2">
            <button
              id="copy-report-btn"
              onClick={handleCopy}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all"
              style={{ background: 'rgba(124,77,255,0.1)', color: '#b8a5ff', border: '1px solid rgba(124,77,255,0.25)' }}
            >
              {copied ? <Check size={14} /> : <Copy size={14} />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button
              id="download-report-btn"
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all"
              style={{ background: 'rgba(96,165,250,0.1)', color: '#60a5fa', border: '1px solid rgba(96,165,250,0.25)' }}
            >
              <Download size={14} />
              Download
            </button>
          </div>
        </div>
      </div>

      {/* Report Content */}
      <div
        className="glass-card p-8 mb-8 md-report"
      >
        {report ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {report}
          </ReactMarkdown>
        ) : (
          <div className="text-center py-8">
            <AlertTriangle size={28} className="mx-auto mb-3" style={{ color: '#fbbf24' }} />
            <p style={{ color: '#c4c2e0' }}>Report returned empty. Please check backend logs.</p>
          </div>
        )}
      </div>

      {/* New Session Button */}
      <div className="text-center">
        <button
          id="new-session-btn"
          onClick={onNewSession}
          className="btn-primary mx-auto"
        >
          <RotateCcw size={16} />
          Launch New Research Session
        </button>
      </div>
    </div>
  )
}

// ─── Error Banner ─────────────────────────────────────────────────────────────

function ErrorBanner({ message, onDismiss }: { message: string; onDismiss: () => void }) {
  return (
    <div
      className="fixed top-5 right-5 z-50 max-w-md p-4 rounded-2xl flex items-start gap-3 animate-slide-right"
      style={{ background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.35)', backdropFilter: 'blur(20px)' }}
    >
      <AlertTriangle size={18} style={{ color: '#f87171', flexShrink: 0, marginTop: 2 }} />
      <div className="flex-1">
        <div className="text-sm font-semibold mb-1" style={{ color: '#f87171' }}>Error</div>
        <div className="text-xs" style={{ color: '#c4c2e0' }}>{message}</div>
      </div>
      <button onClick={onDismiss} style={{ color: '#6b6898' }}>
        <XCircle size={16} />
      </button>
    </div>
  )
}

// ─── Topbar ───────────────────────────────────────────────────────────────────

function Topbar({ stage }: { stage: Stage }) {
  const labels: Record<Stage, string> = {
    search:   'New Research Query',
    scanning: 'Agent Scan In Progress',
    review:   'Human-in-the-Loop Verification',
    report:   'R&D Intelligence Briefing',
  }
  return (
    <header
      className="sticky top-0 z-40 flex items-center justify-between px-6 h-14"
      style={{
        background: 'rgba(6,5,15,0.85)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(124,77,255,0.1)',
      }}
    >
      <div className="flex items-center gap-3">
        <div className="lg:hidden flex items-center gap-2">
          <FlaskConical size={18} style={{ color: '#7c4dff' }} />
          <span className="text-sm font-bold" style={{ color: '#e8e6f8' }}>Innovation Scout</span>
        </div>
        <div
          className="hidden sm:block w-px h-5 mx-1"
          style={{ background: 'rgba(124,77,255,0.2)' }}
        />
        <span className="hidden sm:block text-sm" style={{ color: '#6b6898' }}>
          {labels[stage]}
        </span>
      </div>
      <div
        className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs"
        style={{ background: 'rgba(124,77,255,0.08)', color: '#9474ff', border: '1px solid rgba(124,77,255,0.15)' }}
      >
        <Zap size={11} />
        Powered by LangGraph + Gemini
      </div>
    </header>
  )
}

// ─── App Root ─────────────────────────────────────────────────────────────────

export default function App() {
  const [stage, setStage]         = useState<Stage>('search')
  const [query, setQuery]         = useState('')
  const [searchData, setSearchData] = useState<SearchData | null>(null)
  const [finalReport, setFinalReport] = useState('')
  const [error, setError]         = useState('')
  const [isApproving, setIsApproving] = useState(false)

  const handleSearch = async (q: string) => {
    setQuery(q)
    setError('')
    setStage('scanning')

    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q }),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(`Backend error (${res.status}): ${text}`)
      }

      const data: SearchData = await res.json()
      setSearchData(data)
      setStage('review')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Connection error to FastAPI server.'
      setError(msg)
      setStage('search')
    }
  }

  const handleApprove = async () => {
    if (!searchData) return
    setIsApproving(true)
    setError('')

    try {
      const res = await fetch(`${API_BASE}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: searchData.session_id, approve: true }),
      })

      if (!res.ok) {
        const text = await res.text()
        throw new Error(`Approval failed (${res.status}): ${text}`)
      }

      const data = await res.json()
      setFinalReport(data.final_report || '')
      setStage('report')
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error submitting approval.'
      setError(msg)
    } finally {
      setIsApproving(false)
    }
  }

  const handleReject = () => {
    setSearchData(null)
    setQuery('')
    setError('')
    setStage('search')
  }

  const handleNewSession = () => {
    setSearchData(null)
    setFinalReport('')
    setQuery('')
    setError('')
    setStage('search')
  }

  return (
    <div className="flex min-h-screen" style={{ background: 'var(--color-surface-950)' }}>
      {/* Background glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 80% 60% at 50% -20%, rgba(124,77,255,0.12) 0%, transparent 70%)',
        }}
      />

      <Sidebar stage={stage} />

      <div className="flex-1 flex flex-col min-h-screen">
        <Topbar stage={stage} />

        <main className="flex-1 relative">
          {stage === 'search' && (
            <SearchStage onSearch={handleSearch} />
          )}
          {stage === 'scanning' && (
            <ScanningStage query={query} />
          )}
          {stage === 'review' && searchData && (
            <ReviewStage
              data={searchData}
              onApprove={handleApprove}
              onReject={handleReject}
              isApproving={isApproving}
            />
          )}
          {stage === 'report' && (
            <ReportStage report={finalReport} onNewSession={handleNewSession} />
          )}
        </main>
      </div>

      {/* Global Error Banner */}
      {error && (
        <ErrorBanner message={error} onDismiss={() => setError('')} />
      )}
    </div>
  )
}
