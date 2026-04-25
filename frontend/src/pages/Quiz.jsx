import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

const LEVEL_LABELS = {
  1: '🇫🇷 French',
  2: '📗 Simple English',
  3: '📘 Exam English',
}

export default function Quiz() {
  const { moduleId } = useParams()
  const nav = useNavigate()
  const user = localStorage.getItem('user_name')

  const [q, setQ] = useState(null)
  const [selected, setSelected] = useState(null)
  const [answered, setAnswered] = useState(false)
  const [showFeedback, setShowFeedback] = useState(false)
  const [complete, setComplete] = useState(false)

  const loadNext = () => {
    setSelected(null)
    setAnswered(false)
    setShowFeedback(false)
    fetch(`/api/modules/${moduleId}/next-question?user_name=${encodeURIComponent(user)}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.module_complete) setComplete(true)
        else setQ(data)
      })
  }

  useEffect(() => {
    if (!user) { nav('/'); return }
    loadNext()
  }, [])

  const handleSelect = (idx) => {
    if (answered) return
    setSelected(idx)
    setAnswered(true)
    if (idx === q.correct) {
      setShowFeedback(true)
    } else {
      // Wrong — send immediately with no feedback
      fetch('/api/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_name: user, question_id: q.question_id, selected: idx, feedback: null }),
      })
    }
  }

  const handleFeedback = (feedback) => {
    fetch('/api/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_name: user, question_id: q.question_id, selected, feedback }),
    }).then(() => loadNext())
  }

  const handleNextAfterWrong = () => loadNext()

  if (complete) {
    return (
      <div className="container complete-screen">
        <div className="emoji">🎉</div>
        <h1>Module Complete!</h1>
        <p style={{ margin: '1rem 0', color: '#666' }}>
          You've mastered all questions at exam level.
        </p>
        <button className="btn btn-primary" onClick={() => nav('/modules')}>
          Back to Modules
        </button>
      </div>
    )
  }

  if (!q) return <div className="container">Loading...</div>

  const isCorrect = answered && selected === q.correct
  const isWrong = answered && selected !== q.correct

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <button className="btn" onClick={() => nav('/modules')} style={{ padding: '0.4rem 1rem', fontSize: '0.9rem' }}>
          ← Back
        </button>
        <span className={`level-badge level-${q.level}`}>{LEVEL_LABELS[q.level]}</span>
      </div>

      <div className="card" style={{ cursor: 'default' }}>
        <p style={{ fontSize: '1.1rem', lineHeight: 1.5 }}>{q.question}</p>
      </div>

      {q.options.map((opt, i) => {
        let cls = 'option-btn'
        if (answered) {
          if (i === q.correct) cls += ' correct'
          else if (i === selected) cls += ' wrong'
        } else if (i === selected) {
          cls += ' selected'
        }
        return (
          <button key={i} className={cls} onClick={() => handleSelect(i)}>
            {String.fromCharCode(65 + i)}. {opt}
          </button>
        )
      })}

      {isWrong && (
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <p style={{ color: '#ef4444', fontWeight: 600, marginBottom: '0.8rem' }}>
            Incorrect — the correct answer is highlighted above.
          </p>
          <button className="btn btn-primary" onClick={handleNextAfterWrong}>Next Question</button>
        </div>
      )}

      {showFeedback && (
        <div className="feedback-overlay">
          <div className="feedback-card">
            <h3>Correct! How did you feel?</h3>
            <p style={{ color: '#666', marginBottom: '1rem', fontSize: '0.9rem' }}>
              Did you feel confident about this one?
            </p>
            <div>
              <button className="emoji-btn" onClick={() => handleFeedback('sad')} title="Not confident">😟</button>
              <button className="emoji-btn" onClick={() => handleFeedback('happy')} title="Confident!">😊</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
