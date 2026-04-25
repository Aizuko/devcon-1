import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Modules() {
  const [modules, setModules] = useState([])
  const nav = useNavigate()
  const user = localStorage.getItem('user_name')

  useEffect(() => {
    if (!user) { nav('/'); return }
    fetch('/api/modules')
      .then((r) => r.json())
      .then(async (mods) => {
        const withStatus = await Promise.all(
          mods.map(async (m) => {
            const s = await fetch(`/api/modules/${m.id}/status?user_name=${encodeURIComponent(user)}`).then((r) => r.json())
            return { ...m, ...s }
          })
        )
        setModules(withStatus)
      })
  }, [])

  return (
    <div className="container">
      <h1>📚 Modules</h1>
      <h2>Hi {user} — pick a module to study</h2>
      {modules.map((m) => (
        <div key={m.id} className="card" onClick={() => nav(`/quiz/${m.id}`)}>
          <strong>Module {m.id}: {m.name}</strong>
          <div style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.3rem' }}>
            {m.question_count} questions · {m.percent ?? 0}% complete
          </div>
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: `${m.percent ?? 0}%` }} />
          </div>
        </div>
      ))}
    </div>
  )
}
