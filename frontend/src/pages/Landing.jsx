import React from 'react'
import { Link } from 'react-router-dom'
import { ShieldCheck, ScanLine, FileText } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      <header className="bg-brand-600 text-white p-6">
        <div className="max-w-4xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <ShieldCheck size={32} /> ComplyScan
          </h1>
          <Link to="/auth" className="bg-white text-brand-600 px-4 py-2 rounded-full font-semibold hover:bg-brand-50 transition">
            Officer Portal
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-16 text-center">
        <h2 className="text-4xl font-extrabold text-slate-900 mb-6">
          AI-Powered Legal Metrology Inspection
        </h2>
        <p className="text-lg text-slate-600 mb-12 max-w-2xl mx-auto">
          Automate the verification of Packaged Commodities (Rules, 2011) directly from your smartphone. 
          Capture labels, instantly analyze declarations, and generate official PDF reports.
        </p>

        <div className="grid md:grid-cols-3 gap-8 mb-16 text-left">
          <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100 shadow-sm">
            <ScanLine className="text-brand-500 mb-4" size={40} />
            <h3 className="text-xl font-bold mb-2">1. Smart Scan</h3>
            <p className="text-slate-600">Advanced OCR extracts text, multiple languages, and formats instantly from curved packaging.</p>
          </div>
          <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100 shadow-sm">
            <ShieldCheck className="text-brand-500 mb-4" size={40} />
            <h3 className="text-xl font-bold mb-2">2. Rule Validation</h3>
            <p className="text-slate-600">Cross-checks MRP, Net Quantity, and exact SI Units against the Legal Metrology database.</p>
          </div>
          <div className="p-6 bg-slate-50 rounded-2xl border border-slate-100 shadow-sm">
            <FileText className="text-brand-500 mb-4" size={40} />
            <h3 className="text-xl font-bold mb-2">3. Official Reports</h3>
            <p className="text-slate-600">Generates downloadable PDFs with the exact violation clauses ready for legal notices.</p>
          </div>
        </div>

        <Link to="/auth" className="inline-block bg-brand-600 text-white px-8 py-4 rounded-full font-bold text-lg hover:bg-brand-700 shadow-lg transition transform hover:-translate-y-1">
          Launch Officer Web App
        </Link>
      </main>
    </div>
  )
}
