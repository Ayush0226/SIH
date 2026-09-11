import React, { useState } from 'react'
import { supabase } from '../supabaseClient'
import { ShieldCheck, Lock, Mail, ChevronRight, AlertCircle } from 'lucide-react'

export default function Auth() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAuth = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    
    try {
      if (isLogin) {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
      } else {
        const { error } = await supabase.auth.signUp({ email, password })
        if (error) throw error
        else alert('Registration successful! You can now securely log in.')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-brand-50 via-slate-100 to-brand-100 p-6 relative overflow-hidden">
      
      {/* Decorative background blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-brand-500 opacity-10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-brand-700 opacity-10 rounded-full blur-3xl"></div>

      <div className="w-full max-w-5xl flex rounded-3xl shadow-2xl overflow-hidden glass-card relative z-10">
        
        {/* Left Side: Branding / Info */}
        <div className="hidden lg:flex lg:w-1/2 bg-brand-600 p-12 flex-col justify-between relative overflow-hidden text-white">
          <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-10"></div>
          
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-12">
              <div className="bg-white p-2 rounded-xl">
                <ShieldCheck className="text-brand-600 w-8 h-8" />
              </div>
              <h1 className="text-3xl font-extrabold tracking-tight">ComplyScan</h1>
            </div>
            <h2 className="text-4xl font-bold mb-6 leading-tight">
              Official Legal Metrology Inspection Portal
            </h2>
            <p className="text-brand-100 text-lg leading-relaxed mb-8">
              Securely authenticate to access your officer dashboard. 
              Upload commodity labels, run AI-powered compliance checks, 
              and generate legal PDF notices instantly.
            </p>
          </div>
          
          <div className="relative z-10 bg-brand-700/50 p-6 rounded-2xl border border-brand-500/30">
            <p className="text-sm text-brand-100 font-medium">
              "This system is strictly for authorized Legal Metrology personnel under the Ministry of Consumer Affairs."
            </p>
          </div>
        </div>

        {/* Right Side: Form */}
        <div className="w-full lg:w-1/2 p-8 sm:p-12 bg-white flex flex-col justify-center">
          <div className="mb-10 text-center lg:text-left">
            <h3 className="text-3xl font-bold text-slate-900 mb-2">
              {isLogin ? 'Welcome Back' : 'Create Account'}
            </h3>
            <p className="text-slate-500 font-medium">
              {isLogin ? 'Enter your official credentials to continue.' : 'Register a new officer account.'}
            </p>
          </div>

          <form onSubmit={handleAuth} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-100 p-4 rounded-xl flex items-start gap-3 text-red-800 text-sm font-medium animate-in slide-in-from-top-2">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <p>{error}</p>
              </div>
            )}
            
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-700 ml-1">Official Email Address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-400" />
                </div>
                <input 
                  type="email" 
                  required 
                  className="block w-full pl-11 pr-4 py-3.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all font-medium text-slate-900" 
                  placeholder="officer@gov.in"
                  value={email} 
                  onChange={e => setEmail(e.target.value)} 
                />
              </div>
            </div>

            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-700 ml-1">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400" />
                </div>
                <input 
                  type="password" 
                  required 
                  className="block w-full pl-11 pr-4 py-3.5 rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all font-medium text-slate-900" 
                  placeholder="••••••••"
                  value={password} 
                  onChange={e => setPassword(e.target.value)} 
                />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading} 
              className="w-full flex items-center justify-center gap-2 py-4 px-4 rounded-xl shadow-lg shadow-brand-500/30 text-white bg-brand-600 hover:bg-brand-700 active:scale-[0.98] transition-all font-bold text-lg disabled:opacity-70 disabled:active:scale-100"
            >
              {loading ? 'Authenticating...' : (isLogin ? 'Secure Sign In' : 'Register Account')}
              {!loading && <ChevronRight className="w-5 h-5" />}
            </button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-slate-500 text-sm font-medium">
              {isLogin ? "Don't have access?" : "Already registered?"}{' '}
              <button 
                onClick={() => { setIsLogin(!isLogin); setError(''); }} 
                className="text-brand-600 hover:text-brand-800 font-bold underline decoration-brand-600/30 underline-offset-4 transition"
              >
                {isLogin ? 'Request an account' : 'Sign In instead'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
