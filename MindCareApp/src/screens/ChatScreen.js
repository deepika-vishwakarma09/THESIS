// src/screens/ChatScreen.js — Web-optimized
import React, { useState, useRef, useEffect } from 'react';
import { Alert } from 'react-native';
import { sendMessage, analyzeSession } from '../services/api';
 
export default function ChatScreen({ navigation, route }) {
  const { moodLevel, moodLabel, moodEmoji, moodColor } = route.params;
  const [messages, setMessages]       = useState([]);
  const [inputText, setInputText]     = useState('');
  const [isLoading, setIsLoading]     = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [sessionId, setSessionId]     = useState(null);
  const [msgCount, setMsgCount]       = useState(0);
  const bottomRef = useRef(null);
 
  useEffect(() => {
    setMessages([{
      id: '0', role: 'assistant',
      text: `Hello! I'm your AI companion 💙\n\nI can see you're feeling ${moodLabel} ${moodEmoji} today. I'm here to listen — tell me what's been on your mind lately?`,
    }]);
  }, []);
 
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);
 
  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;
    const userText = inputText.trim();
    setInputText('');
    setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', text: userText }]);
    setIsLoading(true);
    try {
      const res = await sendMessage(userText, sessionId, moodLabel, moodLevel);
      setSessionId(res.session_id);
      setMsgCount(res.message_count);
      setMessages(prev => [...prev, { id: (Date.now()+1).toString(), role: 'assistant', text: res.reply }]);
    } catch {
      setMessages(prev => [...prev, { id: (Date.now()+1).toString(), role: 'assistant', text: "I'm here for you. Tell me more." }]);
    } finally {
      setIsLoading(false);
    }
  };
 
  const handleAnalyze = async () => {
    if (!sessionId) { Alert.alert('Send 2+ messages first!'); return; }
    setIsAnalyzing(true);
    try {
      const result = await analyzeSession(sessionId);
      navigation.navigate('Insights', { analysis: result, moodLevel, moodLabel, moodEmoji, moodColor });
    } catch { Alert.alert('Error', 'Could not analyze!'); }
    finally { setIsAnalyzing(false); }
  };
 
  return (
    <div style={s.page}>
      {/* HEADER */}
      <div style={s.header}>
        <button style={s.backBtn} onClick={() => navigation.goBack()}>←</button>
        <div style={s.botInfo}>
          <div style={s.botIcon}>🧠</div>
          <div>
            <div style={s.botName}>AI Companion</div>
            <div style={s.botStatus}>● Active now</div>
          </div>
        </div>
        <div style={{...s.moodBadge, backgroundColor: moodColor+'20', borderColor: moodColor}}>
          <span>{moodEmoji}</span>
          <span style={{color: moodColor, fontWeight: 700, fontSize: 12}}>{moodLabel}</span>
        </div>
      </div>
 
      {/* MESSAGES */}
      <div style={s.messagesArea}>
        {messages.map(item => {
          const isUser = item.role === 'user';
          return (
            <div key={item.id} style={{...s.row, justifyContent: isUser ? 'flex-end' : 'flex-start'}}>
              {!isUser && <div style={s.avatar}>🧠</div>}
              <div style={{
                ...s.bubble,
                backgroundColor: isUser ? '#667eea' : '#fff',
                color: isUser ? '#fff' : '#374151',
                borderBottomRightRadius: isUser ? 4 : 18,
                borderBottomLeftRadius: isUser ? 18 : 4,
                boxShadow: isUser ? 'none' : '0 2px 8px rgba(0,0,0,0.08)',
              }}>
                {item.text}
              </div>
            </div>
          );
        })}
 
        {isLoading && (
          <div style={{...s.row, justifyContent: 'flex-start'}}>
            <div style={s.avatar}>🧠</div>
            <div style={{...s.bubble, backgroundColor: '#fff', color: '#667eea'}}>● ● ●</div>
          </div>
        )}
 
        {msgCount >= 2 && !isAnalyzing && (
          <button style={s.analyzeBtn} onClick={handleAnalyze}>
            🔍 Analyze My Feelings
          </button>
        )}
 
        {isAnalyzing && (
          <div style={s.analyzingRow}>
            <span style={{color: '#667eea', fontWeight: 700}}>⏳ Analyzing...</span>
          </div>
        )}
 
        <div ref={bottomRef} />
      </div>
 
      {/* INPUT BAR */}
      <div style={s.inputBar}>
        <input
          style={s.input}
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && handleSend()}
          placeholder="Share how you're feeling..."
        />
        <button
          style={{...s.sendBtn, opacity: (!inputText.trim() || isLoading) ? 0.5 : 1}}
          onClick={handleSend}
          disabled={!inputText.trim() || isLoading}
        >➤</button>
      </div>
      <div style={s.privacy}>🔒 Safe & Confidential</div>
    </div>
  );
}
 
const s = {
  page:         { display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#F8FAFB', fontFamily: 'sans-serif', overflow: 'hidden' },
  header:       { display: 'flex', flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', padding: '10px 14px', borderBottom: '1px solid #F0F2F5', gap: 10, flexShrink: 0 },
  backBtn:      { backgroundColor: '#F0F2F5', border: 'none', borderRadius: 10, width: 36, height: 36, fontSize: 18, cursor: 'pointer', fontWeight: 700 },
  botInfo:      { display: 'flex', flexDirection: 'row', alignItems: 'center', gap: 10, flex: 1 },
  botIcon:      { width: 38, height: 38, borderRadius: 12, backgroundColor: '#667eea', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 },
  botName:      { fontSize: 14, fontWeight: 800, color: '#1a1a2e' },
  botStatus:    { fontSize: 11, color: '#10B981', fontWeight: 700 },
  moodBadge:    { display: 'flex', flexDirection: 'row', alignItems: 'center', gap: 5, borderRadius: 20, padding: '4px 12px', border: '1.5px solid', fontSize: 13 },
  messagesArea: { flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column', gap: 12 },
  row:          { display: 'flex', flexDirection: 'row', alignItems: 'flex-end', gap: 8 },
  avatar:       { width: 30, height: 30, borderRadius: 10, backgroundColor: '#667eea', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 15, flexShrink: 0 },
  bubble:       { maxWidth: '75%', padding: '12px 16px', borderRadius: 18, fontSize: 14, lineHeight: 1.55, whiteSpace: 'pre-wrap' },
  analyzeBtn:   { backgroundColor: '#11998e', color: '#fff', border: 'none', borderRadius: 14, padding: '14px 20px', fontSize: 15, fontWeight: 800, cursor: 'pointer', margin: '10px 0', width: '100%' },
  analyzingRow: { display: 'flex', justifyContent: 'center', padding: 8 },
  inputBar:     { display: 'flex', flexDirection: 'row', alignItems: 'center', gap: 8, padding: '10px 14px', backgroundColor: '#fff', borderTop: '1px solid #F0F2F5', flexShrink: 0 },
  input:        { flex: 1, backgroundColor: '#F8FAFB', borderRadius: 24, padding: '10px 18px', fontSize: 14, color: '#374151', border: '1.5px solid #EEF0F5', outline: 'none', fontFamily: 'sans-serif' },
  sendBtn:      { width: 42, height: 42, borderRadius: 21, backgroundColor: '#667eea', color: '#fff', border: 'none', fontSize: 16, cursor: 'pointer' },
  privacy:      { textAlign: 'center', fontSize: 10, color: '#CBD5E1', padding: '4px 0', backgroundColor: '#fff', flexShrink: 0 },
};