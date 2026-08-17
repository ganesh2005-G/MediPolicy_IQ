import React, { useState } from 'react';
import { ragAPI } from '../services/api';
import { Bot, Send, User, Sparkles, BookOpen } from 'lucide-react';

const AiAssistant = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [chat, setChat] = useState([
    { role: 'assistant', text: 'Hello! I am MediPolicy_IQ AI Policy Assistant. Ask me anything about room rent limits, pre-authorization guidelines, or coverage exclusions.', sources: [] }
  ]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    const userMsg = { role: 'user', text: query };
    setChat((prev) => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const res = await ragAPI.queryPolicy(query);
      const botMsg = { role: 'assistant', text: res.answer, sources: res.sources || [] };
      setChat((prev) => [...prev, botMsg]);
    } catch (err) {
      setChat((prev) => [...prev, { role: 'assistant', text: 'Failed to retrieve answer from AI Knowledge base.', sources: [] }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(139, 92, 246, 0.1)', padding: '0.4rem 0.9rem', borderRadius: 'var(--radius-full)', color: 'var(--accent-purple)', fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.75rem' }}>
          <Sparkles size={16} /> Retrieval-Augmented Generation (RAG) Policy Assistant
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: '800' }}>AI Policy Query Assistant</h1>
        <p style={{ color: 'var(--text-secondary)' }}>Instant natural language clarification for insurance policy terms & coverage terms</p>
      </div>

      <div className="glass-card" style={{ height: '550px', display: 'flex', flexDirection: 'column', padding: '1.5rem' }}>
        {/* Chat History Messages */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem', paddingRight: '0.5rem' }}>
          {chat.map((msg, idx) => (
            <div key={idx} style={{
              display: 'flex',
              gap: '0.75rem',
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%'
            }}>
              {msg.role === 'assistant' && (
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--gradient-brand)', display: 'flex', alignItems: 'center', justifyContent: 'center', shrink: 0 }}>
                  <Bot size={18} color="#fff" />
                </div>
              )}

              <div style={{
                background: msg.role === 'user' ? 'var(--gradient-brand)' : 'rgba(255,255,255,0.04)',
                border: msg.role === 'user' ? 'none' : '1px solid var(--border-color)',
                padding: '0.85rem 1.1rem',
                borderRadius: 'var(--radius-md)',
                color: '#fff',
                fontSize: '0.925rem'
              }}>
                <p>{msg.text}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div style={{ marginTop: '0.75rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.1)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    <strong style={{ color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <BookOpen size={12} /> Knowledge Sources:
                    </strong>
                    {msg.sources.map((s, i) => (
                      <div key={i} style={{ marginTop: '0.25rem' }}>• {s}</div>
                    ))}
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', shrink: 0 }}>
                  <User size={18} color="#fff" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', gap: '0.75rem', alignSelf: 'flex-start' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--gradient-brand)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Bot size={18} color="#fff" />
              </div>
              <div style={{ background: 'rgba(255,255,255,0.04)', padding: '0.85rem 1.1rem', borderRadius: 'var(--radius-md)', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Searching policy clauses and synthesizing response...
              </div>
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <input
            type="text"
            className="input-field"
            placeholder="Ask a question (e.g., 'What is the daily room rent cap for POL-1001?')"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            <Send size={18} /> Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default AiAssistant;
