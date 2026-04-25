import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Modules from './pages/Modules'
import Quiz from './pages/Quiz'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/modules" element={<Modules />} />
      <Route path="/quiz/:moduleId" element={<Quiz />} />
    </Routes>
  </BrowserRouter>
)
