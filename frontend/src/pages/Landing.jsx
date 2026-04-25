import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

const LANGUAGES = [
  { code: 'fr', label: '🇫🇷 Français' },
]

export default function Landing() {
  const [name, setName] = useState('')
  const [step, setStep] = useState('name') // 'name' | 'language'
  const nav = useNavigate()

  const handleName = (e) => {
    e.preventDefault()
    if (!name.trim()) return
    localStorage.setItem('user_name', name.trim())
    setStep('language')
  }

  const pickLang = (code) => {
    localStorage.setItem('language', code)
    nav('/modules')
  }

  if (step === 'language') {
    return (
      <div className="container">
        <h1>Welcome, {name}!</h1>
        <h2>Choose your study language</h2>
        <div className="lang-grid">
          {LANGUAGES.map((l) => (
            <button key={l.code} className="lang-btn" onClick={() => pickLang(l.code)}>
              {l.label}
            </button>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <h1>🛡️ SecurityPrep</h1>
      <h2>Alberta Security Guard Exam Trainer</h2>
      <p style={{ margin: '1.5rem 0', color: '#666' }}>
        Practice exam questions starting in your language, then progress to English.
      </p>
      <form onSubmit={handleName}>
        <input
          type="text"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
        />
        <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>
          Start
        </button>
      </form>
    </div>
  )
}
