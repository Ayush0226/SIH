import React from 'react'
import { Link } from 'react-router-dom'
import { ShieldCheck, ScanLine, FileText, ArrowRight, CheckCircle2 } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen bg-slate-50 font-sans selection:bg-brand-500 selection:text-white">
      
      {/* Navigation */}
      <nav className="fixed w-full z-50 glass-card bg-white/80 border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-brand-600 p-2 rounded-lg">
              <ShieldCheck className="text-white w-6 h-6" />
            </div>
            <span className="text-xl font-bold text-slate-900 tracking-tight">ComplyScan</span>
          </div>
          <Link to="/auth" className="flex items-center gap-2 bg-slate-900 text-white px-5 py-2.5 rounded-full font-semibold hover:bg-brand-600 transition-colors shadow-sm">
            Officer Portal <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] opacity-20 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-r from-brand-400 to-blue-600 rounded-full blur-3xl"></div>
        </div>

        <div className="relative max-w-6xl mx-auto px-6 text-center z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-50 border border-brand-100 text-brand-700 text-sm font-semibold mb-8">
            <span className="flex h-2 w-2 rounded-full bg-brand-600"></span>
            Smart India Hackathon 2026 Solution
          </div>
          
          <h1 className="text-5xl lg:text-7xl font-extrabold text-slate-900 tracking-tight mb-8 leading-[1.1]">
            AI-Powered Legal Metrology <br className="hidden lg:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-blue-500">
              Inspection Platform
            </span>
          </h1>
          
          <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto leading-relaxed">
            Automate the verification of Packaged Commodities (Rules, 2011) directly from your smartphone. 
            Capture labels, instantly analyze declarations, and generate official PDF notices.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link to="/auth" className="w-full sm:w-auto px-8 py-4 bg-brand-600 text-white rounded-full font-bold text-lg shadow-lg shadow-brand-500/30 hover:bg-brand-700 hover:scale-105 transition-all flex items-center justify-center gap-2">
              Launch Web App <ArrowRight className="w-5 h-5" />
            </Link>
            <a href="#features" className="w-full sm:w-auto px-8 py-4 bg-white text-slate-700 border border-slate-200 rounded-full font-bold text-lg shadow-sm hover:bg-slate-50 transition-all">
              Learn More
            </a>
          </div>
        </div>
      </main>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white border-t border-slate-100">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Built for Field Officers</h2>
            <p className="text-slate-500 max-w-2xl mx-auto">Streamline your workflow with tools designed specifically for legal metrology compliance enforcement.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Card 1 */}
            <div className="bg-slate-50 rounded-3xl p-8 border border-slate-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center shadow-sm border border-slate-100 mb-6 text-brand-600">
                <ScanLine size={28} />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">1. Smart Scan OCR</h3>
              <p className="text-slate-600 leading-relaxed mb-6">
                Advanced optical character recognition extracts text, multiple languages, and formats instantly from curved packaging.
              </p>
              <ul className="space-y-2">
                <li className="flex items-center gap-2 text-sm text-slate-700 font-medium"><CheckCircle2 className="w-4 h-4 text-brand-500"/> Extract MRP & Net Qty</li>
                <li className="flex items-center gap-2 text-sm text-slate-700 font-medium"><CheckCircle2 className="w-4 h-4 text-brand-500"/> Identify FSSAI & Mfg Dates</li>
              </ul>
            </div>

            {/* Card 2 */}
            <div className="bg-slate-50 rounded-3xl p-8 border border-slate-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 opacity-5">
                <ShieldCheck size={100} />
              </div>
              <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center shadow-sm border border-slate-100 mb-6 text-brand-600 relative z-10">
                <ShieldCheck size={28} />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3 relative z-10">2. Rule Validation</h3>
              <p className="text-slate-600 leading-relaxed mb-6 relative z-10">
                Cross-checks extracted data against the Legal Metrology (Packaged Commodities) Rules, 2011 standard database.
              </p>
              <ul className="space-y-2 relative z-10">
                <li className="flex items-center gap-2 text-sm text-slate-700 font-medium"><CheckCircle2 className="w-4 h-4 text-brand-500"/> Validates standard SI Units</li>
                <li className="flex items-center gap-2 text-sm text-slate-700 font-medium"><CheckCircle2 className="w-4 h-4 text-brand-500"/> Checks Tax Declarations</li>
              </ul>
            </div>

            {/* Card 3 */}
            <div className="bg-slate-50 rounded-3xl p-8 border border-slate-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <div className="w-14 h-14 bg-brand-600 rounded-2xl flex items-center justify-center shadow-md shadow-brand-500/30 mb-6 text-white">
                <FileText size={28} />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">3. Official PDF Reports</h3>
              <p className="text-slate-600 leading-relaxed mb-6">
                Generates downloadable, court-ready PDFs with the exact violation clauses ready for legal notices and prosecution.
              </p>
              <ul className="space-y-2">
                <li className="flex items-center gap-2 text-sm text-slate-700 font-medium"><CheckCircle2 className="w-4 h-4 text-brand-500"/> Cloud-backed History</li>
                <li className="flex items-center gap-2 text-sm text-slate-700 font-medium"><CheckCircle2 className="w-4 h-4 text-brand-500"/> Printable format</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 py-12 text-center text-slate-400">
        <p className="font-medium text-sm">Developed for Smart India Hackathon 2026 (Problem Statement 26034)</p>
      </footer>
    </div>
  )
}
