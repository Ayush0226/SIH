import React, { useState } from 'react'
import { supabase } from '../supabaseClient'
import { ShieldAlert } from 'lucide-react'

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
        else alert('Signup successful! You can now log in.')
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 px-6">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="text-center text-3xl font-extrabold text-slate-900">
          ComplyScan Portal
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          Secure access for Legal Metrology Officers
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl sm:px-10 border border-slate-100">
          <form className="space-y-6" onSubmit={handleAuth}>
            {error && (
              <div className="bg-red-50 p-4 rounded-lg flex items-start gap-3 text-red-800 text-sm">
                <ShieldAlert size={20} className="shrink-0" />
                <p>{error}</p>
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-slate-700">Email address</label>
              <input type="email" required className="mt-1 block w-full px-4 py-3 rounded-lg border border-slate-200 focus:ring-brand-500 focus:border-brand-500" value={email} onChange={e => setEmail(e.target.value)} />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">Password</label>
              <input type="password" required className="mt-1 block w-full px-4 py-3 rounded-lg border border-slate-200 focus:ring-brand-500 focus:border-brand-500" value={password} onChange={e => setPassword(e.target.value)} />
            </div>

            <button type="submit" disabled={loading} className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-brand-600 hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500 disabled:opacity-50">
              {loading ? 'Authenticating...' : (isLogin ? 'Secure Sign In' : 'Register Account')}
            </button>
          </form>

          <div className="mt-6 text-center">
            <button onClick={() => setIsLogin(!isLogin)} className="text-sm text-brand-600 hover:text-brand-500 font-medium">
              {isLogin ? "Don't have an account? Sign Up" : "Already registered? Sign In"}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
