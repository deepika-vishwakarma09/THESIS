// src/screens/InsightsScreen.js
// Works on BOTH web browser AND phone!
import React from 'react';
import {
  View, Text, ScrollView, TouchableOpacity,
  StyleSheet, StatusBar, Platform,
} from 'react-native';

const STATE_COLORS = {
  Anxiety: '#FF9A3C', Depression: '#9B8ED8',
  Stress: '#FF5E5E', Suicidal: '#FF5E5E', Normal: '#3DC88A',
};

const MOOD_LABELS = {
  1: { label: 'Angry',   emoji: '😡', color: '#FF5E5E' },
  2: { label: 'Anxious', emoji: '😰', color: '#FF9A3C' },
  3: { label: 'Tired',   emoji: '😴', color: '#9B8ED8' },
  4: { label: 'Okay',    emoji: '😐', color: '#4EADE0' },
  5: { label: 'Joyful',  emoji: '😊', color: '#3DC88A' },
  6: { label: 'Happy',   emoji: '😄', color: '#F5C518' },
  7: { label: 'Excited', emoji: '🤩', color: '#4CAF50' },
};

const MOODS = [1, 2, 3, 4, 5, 6, 7];

export default function InsightsScreen({ navigation, route }) {
  const { analysis, moodLevel, moodLabel, moodEmoji, moodColor } = route.params;
  const stateColor    = STATE_COLORS[analysis.mental_state] || '#667eea';
  const moodData      = MOOD_LABELS[analysis.mood_level] || MOOD_LABELS[4];
  const confidencePct = Math.round(analysis.confidence * 100);
  const isWeb         = Platform.OS === 'web';

  // ── Web version ─────────────────────────────────────────
  if (isWeb) {
    return (
      <div style={ws.page}>
        <div style={ws.header}>
          <button style={ws.backBtn} onClick={() => navigation.goBack()}>← Back</button>
          <div style={ws.headerTitle}>Your Mental Health</div>
          <div style={ws.headerSub}>AI Analysis Complete ✓</div>
        </div>

        <div style={ws.scrollArea}>
          <div style={ws.card}>
            <div style={ws.row}>
              <div>
                <div style={ws.label}>MENTAL STATE DETECTED</div>
                <div style={{...ws.stateBadge, backgroundColor: stateColor+'18', borderColor: stateColor+'40'}}>
                  <div style={{...ws.stateDot, backgroundColor: stateColor}} />
                  <span style={{color: stateColor, fontSize: 18, fontWeight: 800}}>{analysis.mental_state}</span>
                </div>
              </div>
              <div style={ws.confBox}>
                <div style={ws.confLabel}>Confidence</div>
                <div style={ws.confVal}>{confidencePct}%</div>
              </div>
            </div>

            <div style={ws.causeBox}>
              <span style={{fontSize: 20}}>⚡</span>
              <div>
                <div style={ws.label}>IDENTIFIED CAUSE</div>
                <div style={ws.causeText}>{analysis.cause}</div>
              </div>
            </div>

            <div style={{...ws.summaryBox, borderLeftColor: stateColor}}>
              <span style={ws.summaryText}>"{analysis.summary}"</span>
            </div>

            <div style={ws.label}>KEY SIGNALS FOUND (SHAP)</div>
            <div style={ws.keywordsRow}>
              {analysis.keywords?.map((kw, i) => (
                <div key={i} style={ws.keyword}>#{kw}</div>
              ))}
            </div>

            <div style={ws.label}>MOOD SCALE (1–7)</div>
            <div style={ws.scaleBar}>
              {MOODS.map(m => (
                <div key={m} style={{...ws.scaleSeg, backgroundColor: m <= analysis.mood_level ? MOOD_LABELS[m].color : '#EEF0F5'}} />
              ))}
            </div>
            <div style={ws.scaleLabels}>
              <span style={ws.scaleLabel}>😡 Angry</span>
              <span style={{color: moodData.color, fontWeight: 700, fontSize: 12}}>{moodData.emoji} {moodData.label} (Level {analysis.mood_level})</span>
              <span style={ws.scaleLabel}>🤩 Excited</span>
            </div>
          </div>

          <div style={ws.tipsCard}>
            <div style={ws.tipsTitle}>💡 Suggested Coping Tips</div>
            {analysis.suggestions?.map((tip, i) => (
              <div key={i} style={ws.tipRow}>
                <div style={ws.tipNum}>{i + 1}</div>
                <div style={ws.tipText}>{tip}</div>
              </div>
            ))}
          </div>

          {analysis.mental_state === 'Suicidal' && (
            <div style={ws.alertBox}>
              <div style={ws.alertTitle}>🚨 Immediate Support Needed</div>
              <div style={ws.alertText}>Please reach out immediately. iCall: 9152987821</div>
            </div>
          )}

          <button style={ws.dashBtn} onClick={() => navigation.navigate('Dashboard', {
            analysis, moodLevel, moodLabel, moodEmoji, moodColor,
          })}>📊 View Your Dashboard</button>

          <div style={ws.privacy}>🔒 Data is private and confidential</div>
        </div>
      </div>
    );
  }

  // ── Phone version (React Native) ────────────────────────
  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#667eea" />
      <ScrollView showsVerticalScrollIndicator={false}>

        {/* Header */}
        <View style={styles.headerGradient}>
          <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Your Mental Health</Text>
          <Text style={styles.headerSub}>AI Analysis Complete ✓</Text>
        </View>

        {/* Main Card */}
        <View style={styles.mainCard}>
          <View style={styles.stateRow}>
            <View>
              <Text style={styles.sectionLabel}>MENTAL STATE DETECTED</Text>
              <View style={[styles.stateBadge, { backgroundColor: stateColor+'18', borderColor: stateColor+'40' }]}>
                <View style={[styles.stateDot, { backgroundColor: stateColor }]} />
                <Text style={[styles.stateText, { color: stateColor }]}>{analysis.mental_state}</Text>
              </View>
            </View>
            <View style={styles.confBox}>
              <Text style={styles.confLabel}>Confidence</Text>
              <Text style={styles.confVal}>{confidencePct}%</Text>
            </View>
          </View>

          <View style={styles.causeBox}>
            <Text style={{ fontSize: 20 }}>⚡</Text>
            <View>
              <Text style={styles.sectionLabel}>IDENTIFIED CAUSE</Text>
              <Text style={styles.causeText}>{analysis.cause}</Text>
            </View>
          </View>

          <View style={[styles.summaryBox, { borderLeftColor: stateColor }]}>
            <Text style={styles.summaryText}>"{analysis.summary}"</Text>
          </View>

          <Text style={styles.sectionLabel}>KEY SIGNALS FOUND (SHAP)</Text>
          <View style={styles.keywordsRow}>
            {analysis.keywords?.map((kw, i) => (
              <View key={i} style={styles.keyword}>
                <Text style={styles.keywordText}>#{kw}</Text>
              </View>
            ))}
          </View>

          <Text style={styles.sectionLabel}>MOOD SCALE (1–7)</Text>
          <View style={styles.scaleBar}>
            {MOODS.map(m => (
              <View key={m} style={[styles.scaleSeg, { backgroundColor: m <= analysis.mood_level ? MOOD_LABELS[m].color : '#EEF0F5' }]} />
            ))}
          </View>
          <View style={styles.scaleLabels}>
            <Text style={styles.scaleLabel}>😡 Angry</Text>
            <Text style={{ color: moodData.color, fontWeight: '700', fontSize: 12 }}>{moodData.emoji} Level {analysis.mood_level}</Text>
            <Text style={styles.scaleLabel}>🤩 Excited</Text>
          </View>
        </View>

        {/* Coping Tips */}
        <View style={styles.tipsCard}>
          <Text style={styles.tipsTitle}>💡 Suggested Coping Tips</Text>
          {analysis.suggestions?.map((tip, i) => (
            <View key={i} style={styles.tipRow}>
              <View style={styles.tipNum}><Text style={styles.tipNumText}>{i + 1}</Text></View>
              <Text style={styles.tipText}>{tip}</Text>
            </View>
          ))}
        </View>

        {analysis.mental_state === 'Suicidal' && (
          <View style={styles.alertBox}>
            <Text style={styles.alertTitle}>🚨 Immediate Support Needed</Text>
            <Text style={styles.alertText}>Please reach out immediately. iCall: 9152987821</Text>
          </View>
        )}

        <TouchableOpacity style={styles.dashBtn} onPress={() => navigation.navigate('Dashboard', {
          analysis, moodLevel, moodLabel, moodEmoji, moodColor,
        })}>
          <Text style={styles.dashBtnText}>📊 View Your Dashboard</Text>
        </TouchableOpacity>

        <Text style={styles.privacy}>🔒 Data is private and confidential</Text>
      </ScrollView>
    </View>
  );
}

// ── Web Styles ──────────────────────────────────────────────
const ws = {
  page:        { display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#F8FAFB', fontFamily: 'sans-serif', overflow: 'hidden' },
  header:      { backgroundColor: '#667eea', padding: '20px 20px 36px', flexShrink: 0 },
  backBtn:     { backgroundColor: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: 10, padding: '6px 14px', color: '#fff', fontSize: 13, cursor: 'pointer', fontWeight: 600, marginBottom: 14, display: 'block' },
  headerTitle: { color: '#fff', fontSize: 24, fontWeight: 800, marginBottom: 4 },
  headerSub:   { color: 'rgba(255,255,255,0.75)', fontSize: 13 },
  scrollArea:  { flex: 1, overflowY: 'auto', padding: '0 16px 30px' },
  card:        { backgroundColor: '#fff', borderRadius: 22, padding: 20, marginTop: -20, boxShadow: '0 10px 40px rgba(0,0,0,0.12)', marginBottom: 14 },
  row:         { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 },
  label:       { fontSize: 10, fontWeight: 700, letterSpacing: 1.5, color: '#9CA3AF', textTransform: 'uppercase', marginBottom: 8, marginTop: 14 },
  stateBadge:  { display: 'inline-flex', alignItems: 'center', gap: 8, borderRadius: 24, padding: '7px 16px', border: '1.5px solid' },
  stateDot:    { width: 9, height: 9, borderRadius: 5 },
  confBox:     { backgroundColor: '#F8FAFB', borderRadius: 14, padding: '10px 14px', textAlign: 'center' },
  confLabel:   { fontSize: 10, color: '#9CA3AF', fontWeight: 600, marginBottom: 2 },
  confVal:     { fontSize: 26, fontWeight: 800, color: '#1a1a2e' },
  causeBox:    { display: 'flex', alignItems: 'center', gap: 12, backgroundColor: '#F8FAFB', borderRadius: 14, padding: 14, marginBottom: 4 },
  causeText:   { fontSize: 16, fontWeight: 700, color: '#374151' },
  summaryBox:  { borderLeft: '3.5px solid', padding: 12, backgroundColor: '#F8FAFB', borderRadius: 8, marginBottom: 4 },
  summaryText: { fontSize: 13, color: '#4B5563', lineHeight: 1.6, fontStyle: 'italic' },
  keywordsRow: { display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 4 },
  keyword:     { backgroundColor: '#EEF2FF', color: '#667eea', padding: '5px 13px', borderRadius: 20, fontSize: 12, fontWeight: 700 },
  scaleBar:    { display: 'flex', gap: 4, marginBottom: 8 },
  scaleSeg:    { flex: 1, height: 10, borderRadius: 5 },
  scaleLabels: { display: 'flex', justifyContent: 'space-between' },
  scaleLabel:  { fontSize: 10, color: '#9CA3AF' },
  tipsCard:    { backgroundColor: '#fff', borderRadius: 20, padding: 18, marginBottom: 14, boxShadow: '0 4px 20px rgba(0,0,0,0.06)' },
  tipsTitle:   { fontSize: 15, fontWeight: 800, color: '#1a1a2e', marginBottom: 16 },
  tipRow:      { display: 'flex', alignItems: 'flex-start', gap: 12, marginBottom: 14 },
  tipNum:      { width: 28, height: 28, borderRadius: 9, backgroundColor: '#667eea', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 800, flexShrink: 0 },
  tipText:     { fontSize: 13, color: '#4B5563', lineHeight: 1.5 },
  alertBox:    { backgroundColor: '#FFF0F0', borderRadius: 16, padding: 16, border: '1.5px solid #FF5E5E', marginBottom: 14 },
  alertTitle:  { fontSize: 14, fontWeight: 800, color: '#B03030', marginBottom: 6 },
  alertText:   { fontSize: 13, color: '#B03030' },
  dashBtn:     { width: '100%', backgroundColor: '#667eea', color: '#fff', border: 'none', borderRadius: 16, padding: 16, fontSize: 16, fontWeight: 800, cursor: 'pointer', marginBottom: 12, boxSizing: 'border-box' },
  privacy:     { textAlign: 'center', fontSize: 11, color: '#CBD5E1', paddingBottom: 10 },
};

// ── Phone Styles ────────────────────────────────────────────
const styles = StyleSheet.create({
  container:     { flex: 1, backgroundColor: '#F8FAFB' },
  headerGradient:{ backgroundColor: '#667eea', padding: 20, paddingTop: 52, paddingBottom: 36 },
  backBtn:       { backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 6, alignSelf: 'flex-start', marginBottom: 14 },
  backText:      { color: '#fff', fontSize: 13, fontWeight: '600' },
  headerTitle:   { color: '#fff', fontSize: 24, fontWeight: '800', marginBottom: 4 },
  headerSub:     { color: 'rgba(255,255,255,0.75)', fontSize: 13 },
  mainCard:      { margin: 16, marginTop: -20, backgroundColor: '#fff', borderRadius: 22, padding: 20, elevation: 10 },
  stateRow:      { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 },
  sectionLabel:  { fontSize: 10, fontWeight: '700', letterSpacing: 1.5, color: '#9CA3AF', textTransform: 'uppercase', marginBottom: 8, marginTop: 14 },
  stateBadge:    { flexDirection: 'row', alignItems: 'center', gap: 8, borderRadius: 24, paddingHorizontal: 16, paddingVertical: 8, borderWidth: 1.5 },
  stateDot:      { width: 9, height: 9, borderRadius: 5 },
  stateText:     { fontSize: 18, fontWeight: '800' },
  confBox:       { backgroundColor: '#F8FAFB', borderRadius: 14, padding: 12, alignItems: 'center' },
  confLabel:     { fontSize: 10, color: '#9CA3AF', fontWeight: '600', marginBottom: 2 },
  confVal:       { fontSize: 26, fontWeight: '800', color: '#1a1a2e' },
  causeBox:      { flexDirection: 'row', alignItems: 'center', gap: 12, backgroundColor: '#F8FAFB', borderRadius: 14, padding: 14, marginBottom: 4 },
  causeText:     { fontSize: 16, fontWeight: '700', color: '#374151' },
  summaryBox:    { borderLeftWidth: 3.5, padding: 12, backgroundColor: '#F8FAFB', borderRadius: 8, marginBottom: 4 },
  summaryText:   { fontSize: 13, color: '#4B5563', lineHeight: 22, fontStyle: 'italic' },
  keywordsRow:   { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 4 },
  keyword:       { backgroundColor: '#EEF2FF', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 6 },
  keywordText:   { fontSize: 12, fontWeight: '700', color: '#667eea' },
  scaleBar:      { flexDirection: 'row', gap: 4, marginBottom: 8 },
  scaleSeg:      { flex: 1, height: 10, borderRadius: 5 },
  scaleLabels:   { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  scaleLabel:    { fontSize: 10, color: '#9CA3AF' },
  tipsCard:      { margin: 16, marginTop: 0, backgroundColor: '#fff', borderRadius: 20, padding: 18, elevation: 4 },
  tipsTitle:     { fontSize: 15, fontWeight: '800', color: '#1a1a2e', marginBottom: 16 },
  tipRow:        { flexDirection: 'row', alignItems: 'flex-start', gap: 12, marginBottom: 14 },
  tipNum:        { width: 28, height: 28, borderRadius: 9, backgroundColor: '#667eea', justifyContent: 'center', alignItems: 'center' },
  tipNumText:    { color: '#fff', fontSize: 12, fontWeight: '800' },
  tipText:       { flex: 1, fontSize: 13, color: '#4B5563', lineHeight: 20 },
  alertBox:      { margin: 16, marginTop: 0, backgroundColor: '#FFF0F0', borderRadius: 16, padding: 16, borderWidth: 1.5, borderColor: '#FF5E5E' },
  alertTitle:    { fontSize: 14, fontWeight: '800', color: '#B03030', marginBottom: 6 },
  alertText:     { fontSize: 13, color: '#B03030', lineHeight: 20 },
  dashBtn:       { margin: 16, backgroundColor: '#667eea', borderRadius: 16, padding: 16, alignItems: 'center', elevation: 8 },
  dashBtnText:   { color: '#fff', fontSize: 16, fontWeight: '800' },
  privacy:       { textAlign: 'center', fontSize: 11, color: '#CBD5E1', marginBottom: 30 },
});