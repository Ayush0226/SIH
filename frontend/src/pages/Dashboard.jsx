import React, { useState, useEffect } from 'react'
import { supabase } from '../supabaseClient'
import { LogOut, Camera, FileText, Upload, AlertCircle, CheckCircle2, ScanLine } from 'lucide-react'

// You would replace this with your deployed Render URL in production
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

export default function Dashboard({ session }) {
  const [activeTab, setActiveTab] = useState('scan')
  const [file, setFile] = useState(null)
  const [category, setCategory] = useState('Food')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])

  const handleLogout = () => supabase.auth.signOut()

  const getPdfUrl = (url) => {
    if (!url) return "#"
    if (url.includes("127.0.0.1:8000")) {
      return url.replace("http://127.0.0.1:8000", API_URL)
    }
    if (!url.startsWith("http")) {
      return `${API_URL}${url}`
    }
    return url
  }

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_URL}/api/history`, {
        headers: { "Authorization": `Bearer ${session.access_token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setHistory(data.history)
      }
    } catch (err) {
      console.error("Failed to fetch history")
    }
  }

  useEffect(() => {
    if (activeTab === 'history') fetchHistory()
  }, [activeTab])

  const handleScan = async (e) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    const formData = new FormData()
    formData.append('category', category)
    formData.append('file', file)

    try {
      const response = await fetch(`${API_URL}/api/analyze`, {
        method: 'POST',
        headers: { "Authorization": `Bearer ${session.access_token}` },
        body: formData
      })
      const data = await response.json()
      setResult(data)
    } catch (err) {
      alert("Error connecting to OCR backend.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-brand-600 text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-xl font-bold flex items-center gap-2">⚖️ ComplyScan</h1>
            <div className="flex items-center gap-4">
              <span className="text-brand-100 hidden sm:block text-sm">{session.user.email}</span>
              <button onClick={handleLogout} className="p-2 hover:bg-brand-700 rounded-full transition"><LogOut size={20} /></button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-slate-200">
          <button onClick={() => setActiveTab('scan')} className={`pb-4 px-4 font-semibold ${activeTab === 'scan' ? 'text-brand-600 border-b-2 border-brand-600' : 'text-slate-500'}`}>New Scan</button>
          <button onClick={() => setActiveTab('history')} className={`pb-4 px-4 font-semibold ${activeTab === 'history' ? 'text-brand-600 border-b-2 border-brand-600' : 'text-slate-500'}`}>Scan History</button>
        </div>

        {activeTab === 'scan' ? (
          <div className="grid md:grid-cols-12 gap-8">
            <div className="md:col-span-4">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <form onSubmit={handleScan} className="space-y-6">
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Product Category</label>
                    <select className="w-full p-3 rounded-lg border border-slate-200 bg-slate-50" value={category} onChange={e => setCategory(e.target.value)}>
                      <option value="Food">Food & Beverage</option>
                      <option value="Cosmetics">Cosmetics & Personal Care</option>
                      <option value="Electronics">Electronics</option>
                      <option value="Apparel">Apparel</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Capture Label</label>
                    <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center bg-slate-50 hover:bg-slate-100 transition relative">
                      <input type="file" accept="image/*" capture="environment" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" onChange={e => setFile(e.target.files[0])} />
                      <Camera className="mx-auto text-slate-400 mb-2" size={32} />
                      <p className="text-sm text-slate-600 font-medium">{file ? file.name : "Tap to open Camera / Upload"}</p>
                    </div>
                  </div>
                  <button type="submit" disabled={!file || loading} className="w-full bg-brand-600 text-white py-4 rounded-xl font-bold shadow-lg hover:bg-brand-700 disabled:opacity-50 transition flex justify-center items-center gap-2">
                    {loading ? "Analyzing via AI..." : <><Upload size={20}/> Analyze Label</>}
                  </button>
                </form>
              </div>
            </div>

            <div className="md:col-span-8">
              {result ? (
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="flex justify-between items-start mb-6">
                    <h2 className="text-2xl font-bold text-slate-900">Inspection Report</h2>
                    <a href={getPdfUrl(result.pdf_url)} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-brand-600 bg-brand-50 px-4 py-2 rounded-full font-semibold hover:bg-brand-100 transition">
                      <FileText size={18}/> PDF
                    </a>
                  </div>

                  <div className={`p-4 rounded-xl mb-6 flex items-center gap-3 ${result.report.status === 'PASS' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                    {result.report.status === 'PASS' ? <CheckCircle2 size={24}/> : <AlertCircle size={24}/>}
                    <span className="font-bold text-lg">VERDICT: {result.report.status}</span>
                  </div>

                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">1. Extracted Data</h3>
                  {Object.entries(result.extracted_data).some(([k, v]) => v && k !== 'mrp_value' && k !== 'net_quantity_value' && v !== 'Unreadable or Blank Image') ? (
                    <div className="grid grid-cols-2 gap-4 mb-8">
                      {Object.entries(result.extracted_data).map(([k, v]) => (
                        v && k !== 'mrp_value' && k !== 'net_quantity_value' ? (
                          <div key={k} className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                            <span className="block text-xs text-slate-500 uppercase font-semibold mb-1">{k.replace(/_/g, ' ')}</span>
                            <span className="block font-medium text-slate-900">{v}</span>
                          </div>
                        ) : null
                      ))}
                    </div>
                  ) : (
                    <div className="p-4 mb-8 bg-amber-50 border border-amber-200 text-amber-900 rounded-xl text-sm font-medium">
                      ⚠️ No clear text could be recognized from this image. Please upload a clear, focused photo of the label declarations.
                    </div>
                  )}

                  <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4">2. Legal Violations Noted</h3>
                  {result.report.violations.length > 0 ? (
                    <ul className="space-y-2">
                      {result.report.violations.map((v, i) => (
                        <li key={i} className="p-3 bg-red-50 text-red-700 rounded-lg text-sm font-medium flex items-start gap-2">
                          <span className="mt-0.5">•</span> {v}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <div className="p-4 bg-green-50 text-green-700 rounded-lg text-sm font-medium">All checked declarations appear compliant.</div>
                  )}
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-400 p-12 text-center bg-white rounded-2xl border border-dashed border-slate-200">
                  <ScanLine size={48} className="mb-4 opacity-50" />
                  <p>Upload a product label to see the detailed OCR extraction and compliance report here.</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
             <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50 text-slate-500 text-sm uppercase">
                    <th className="p-4 font-semibold">Date</th>
                    <th className="p-4 font-semibold">Category</th>
                    <th className="p-4 font-semibold">Status</th>
                    <th className="p-4 font-semibold text-right">Report</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {history.map((scan, i) => (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="p-4 text-slate-900 font-medium">{new Date(scan.created_at).toLocaleDateString()}</td>
                      <td className="p-4 text-slate-600">{scan.category}</td>
                      <td className="p-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${scan.status === 'PASS' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {scan.status}
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <a href={getPdfUrl(scan.pdf_url)} target="_blank" rel="noopener noreferrer" className="text-brand-600 hover:text-brand-700 font-medium text-sm flex items-center justify-end gap-1">
                          <FileText size={16}/> View
                        </a>
                      </td>
                    </tr>
                  ))}
                  {history.length === 0 && (
                    <tr><td colSpan="4" className="p-8 text-center text-slate-400">No scans found in database.</td></tr>
                  )}
                </tbody>
             </table>
          </div>
        )}
      </div>
    </div>
  )
}
