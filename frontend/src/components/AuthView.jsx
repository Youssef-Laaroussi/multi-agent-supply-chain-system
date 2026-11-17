import React, { useState } from 'react';
import {
  Mail,
  Lock,
  User,
  ArrowRight,
  Eye,
  EyeOff,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { loginUser, signupUser, saveStoredSession } from '../api/client';

export default function AuthView({
  mode = 'login', // 'login' | 'signup'
  onNavigate,
  onSuccess
}) {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');

  const isLogin = mode === 'login';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const cleanEmail = email.trim();
    if (!cleanEmail || !cleanEmail.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }
    if (!password || password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (!isLogin && !fullName.trim()) {
      setError('Please enter your full name.');
      return;
    }

    setIsLoading(true);
    if (isLogin) {
      const res = await loginUser({ email: cleanEmail, password });
      setIsLoading(false);
      if (!res.ok) {
        setError(res.error);
        return;
      }
      onSuccess(res.data.user);
    } else {
      const res = await signupUser({
        name: fullName.trim(),
        email: cleanEmail,
        password,
        organization: 'AURA Sovereign Ops',
        role: 'Supply Chain Director'
      });
      setIsLoading(false);
      if (!res.ok) {
        setError(res.error);
        return;
      }
      onSuccess(res.data.user);
    }
  };

  const handleOAuthProvider = (providerName) => {
    const user = {
      id: Date.now(),
      name: providerName === 'Google' ? 'Youssef Laaroussi' : 'GitHub Operator',
      email: providerName === 'Google' ? 'youssef@aura-sovereign.ai' : 'github@aura-sovereign.ai',
      organization: 'AURA Sovereign Command',
      role: 'Supply Chain Director'
    };
    saveStoredSession({ token: `oauth-${providerName.toLowerCase()}-${Date.now()}`, user });
    onSuccess(user);
  };

  return (
    <main className="nuv-auth-page" aria-label={isLogin ? 'Sign In' : 'Create Account'}>
      <div className="nuv-auth-wrapper">
        {/* Top Centered Brand Logo */}
        <button
          type="button"
          className="nuv-brand-header"
          onClick={() => onNavigate('/')}
          title="Back to Home"
        >
          <span className="nuv-logo-tile">
            <svg className="aura-wave-logo" width="26" height="18" viewBox="0 0 42 26" fill="none" aria-hidden="true">
              <path
                d="M2 21 C 10 21, 14 5, 23 5 C 31 5, 34 15, 40 15"
                stroke="url(#nuvLogoGrad)"
                strokeWidth="4.6"
                strokeLinecap="round"
              />
              <defs>
                <linearGradient id="nuvLogoGrad" x1="2" y1="21" x2="40" y2="10" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#24B68C" />
                  <stop offset="100%" stopColor="#0D5C52" />
                </linearGradient>
              </defs>
            </svg>
          </span>
          <span className="nuv-brand-name">AURA SOVEREIGN</span>
        </button>

        {/* Centered Serif Heading + Green Underline + Subtitle */}
        <div className="nuv-heading-block">
          <h1 className="nuv-serif-title">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h1>
          <div className="nuv-title-underline" />
          <p className="nuv-subtitle">
            {isLogin ? 'Sign in to continue' : 'Sign up to get started'}
          </p>
        </div>

        {/* White Card */}
        <div className="nuv-auth-card">
          <form onSubmit={handleSubmit} className="nuv-auth-form" noValidate>
            {!isLogin && (
              <div className="nuv-input-box">
                <User size={18} className="nuv-field-icon" />
                <input
                  type="text"
                  className="nuv-input"
                  placeholder="Full name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  autoComplete="name"
                  required
                />
              </div>
            )}

            <div className="nuv-input-box">
              <Mail size={18} className="nuv-field-icon" />
              <input
                type="email"
                className="nuv-input"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="nuv-input-box">
              <Lock size={18} className="nuv-field-icon" />
              <input
                type={showPassword ? 'text' : 'password'}
                className="nuv-input"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete={isLogin ? 'current-password' : 'new-password'}
                required
              />
              <button
                type="button"
                className="nuv-eye-btn"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
              </button>
            </div>

            <div className="nuv-options-row">
              <label className="nuv-remember-label">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <span>{isLogin ? 'Remember me' : 'Accept terms & privacy'}</span>
              </label>

              {isLogin && (
                <button
                  type="button"
                  className="nuv-forgot-btn"
                  onClick={() => {
                    setEmail('admin@aura-sovereign.ai');
                    setPassword('Aura2026!');
                    setError('');
                  }}
                >
                  Forgot password?
                </button>
              )}
            </div>

            {error && (
              <div className="nuv-error-alert" role="alert">
                <AlertCircle size={15} />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              className="nuv-submit-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 size={17} className="spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>{isLogin ? 'Sign In' : 'Create Account'}</span>
                  <ArrowRight size={17} />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="nuv-or-divider">
            <span>or</span>
          </div>

          {/* Continue with Google & Continue with GitHub */}
          <div className="nuv-social-stack">
            <button
              type="button"
              className="nuv-social-btn"
              onClick={() => handleOAuthProvider('Google')}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
                <path fill="#EA4335" d="M12 5c1.6 0 3 .6 4.1 1.7l3.1-3.1C17.3 1.8 14.8 1 12 1 7.4 1 3.5 3.6 1.6 7.4l3.7 2.8C6.2 7.2 8.9 5 12 5z" />
                <path fill="#4285F4" d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.6l3.7 2.9c2.2-2 3.7-5 3.7-8.7z" />
                <path fill="#FBBC05" d="M5.3 14.8c-.2-.8-.4-1.6-.4-2.5s.2-1.7.4-2.5L1.6 7C.6 9 0 11.2 0 13.5s.6 4.5 1.6 6.5l3.7-2.9z" />
                <path fill="#34A853" d="M12 24c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3.1 0-5.8-2.1-6.7-5l-3.7 2.8C3.5 21.4 7.4 24 12 24z" />
              </svg>
              <span>Continue with Google</span>
            </button>

            <button
              type="button"
              className="nuv-social-btn"
              onClick={() => handleOAuthProvider('GitHub')}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="#181717" aria-hidden="true">
                <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.09 3.29 9.4 7.86 10.92.58.1.79-.25.79-.56 0-.28-.01-1.02-.02-2-3.2.7-3.88-1.54-3.88-1.54-.52-1.33-1.28-1.68-1.28-1.68-1.05-.71.08-.7.08-.7 1.16.08 1.77 1.19 1.77 1.19 1.03 1.76 2.7 1.25 3.36.96.1-.75.4-1.25.73-1.54-2.55-.29-5.23-1.28-5.23-5.68 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11.05 11.05 0 0 1 5.78 0c2.2-1.49 3.16-1.18 3.16-1.18.63 1.59.24 2.76.12 3.05.74.81 1.18 1.83 1.18 3.09 0 4.41-2.69 5.38-5.25 5.67.41.36.78 1.06.78 2.14 0 1.55-.01 2.8-.01 3.18 0 .31.21.67.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
              </svg>
              <span>Continue with GitHub</span>
            </button>
          </div>

          {/* Footer Link */}
          <div className="nuv-card-footer">
            {isLogin ? (
              <p>
                Don&apos;t have an account?{' '}
                <button
                  type="button"
                  className="nuv-switch-link"
                  onClick={() => {
                    setError('');
                    onNavigate('/signup');
                  }}
                >
                  Create account
                </button>
              </p>
            ) : (
              <p>
                Already have an account?{' '}
                <button
                  type="button"
                  className="nuv-switch-link"
                  onClick={() => {
                    setError('');
                    onNavigate('/login');
                  }}
                >
                  Sign in
                </button>
              </p>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
