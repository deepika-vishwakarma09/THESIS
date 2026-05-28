
// src/screens/DashboardScreen.js
// ─────────────────────────────────
// Screen 4: Dashboard - Mood trends + Risk alerts
 
import React, { useState, useEffect } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity,
  StyleSheet, StatusBar, ActivityIndicator,
  Dimensions,
} from 'react-native';
import { getDashboard } from '../services/api';
 
const { width } = Dimensions.get('window');
 
// ── Mood data ──────────────────────────────────────────────
const MOOD_LABELS = {
  1: { label: 'Angry',   emoji: '😡', color: '#FF5E5E' },
  2: { label: 'Anxious', emoji: '😰', color: '#FF9A3C' },
  3: { label: 'Tired',   emoji: '😴', color: '#9B8ED8' },
  4: { label: 'Okay',    emoji: '😐', color: '#4EADE0' },
  5: { label: 'Joyful',  emoji: '😊', color: '#3DC88A' },
  6: { label: 'Happy',   emoji: '😄', color: '#F5C518' },
  7: { label: 'Excited', emoji: '🤩', color: '#4CAF50' },
};
 
const STATE_COLORS = {
  Anxiety:    '#FF9A3C',
  Depression: '#9B8ED8',
  Stress:     '#FF5E5E',
  Suicidal:   '#FF5E5E',
  Normal:     '#3DC88A',
};
 
export default function DashboardScreen({ navigation, route }) {
  const { analysis, moodLevel, moodLabel, moodEmoji } = route.params;
 
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading]     = useState(true);
 
  useEffect(() => {
    loadDashboard();
  }, []);
 
  const loadDashboard = async () => {
    try {
      const data = await getDashboard();
      setDashboard(data);
    } catch (e) {
      console.log('Dashboard error:', e);
    } finally {
      setLoading(false);
    }
  };
 
  // ── Simple Bar Chart ───────────────────────────────────
  const MoodChart = ({ weekData }) => {
    const maxLevel = 7;
    const chartHeight = 120;
 
    return (
      <View style={styles.chartContainer}>
        {weekData.map((day, i) => {
          const moodInfo  = MOOD_LABELS[day.mood_level] || MOOD_LABELS[4];
          const barHeight = (day.mood_level / maxLevel) * chartHeight;
 
          return (
            <View key={i} style={styles.chartBar}>
              <Text style={styles.chartEmoji}>{moodInfo.emoji}</Text>
              <View style={styles.chartBarBg}>
                <View
                  style={[
                    styles.chartBarFill,
                    { height: barHeight, backgroundColor: moodInfo.color },
                  ]}
                />
              </View>
              <Text style={styles.chartDay}>{day.day}</Text>
            </View>
          );
        })}
      </View>
    );
  };
 
  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#667eea" />
        <Text style={styles.loadingText}>Loading dashboard...</Text>
      </View>
    );
  }
 
  const weekData    = dashboard?.week_data || [];
  const streak      = dashboard?.streak || 0;
  const avgMood     = dashboard?.avg_mood || 0;
  const avgMoodData = MOOD_LABELS[Math.round(avgMood)] || MOOD_LABELS[4];
  const riskAlert   = dashboard?.risk_alert || false;
  const riskState   = dashboard?.risk_state || '';
  const stateColor  = STATE_COLORS[analysis?.mental_state] || '#667eea';
 
  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#667eea" />
 
      <ScrollView showsVerticalScrollIndicator={false}>
 
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.headerGreeting}>Good day 👋</Text>
              <Text style={styles.headerTitle}>Mood Dashboard</Text>
              <View style={styles.todayMoodBadge}>
                <Text style={{ fontSize: 16 }}>{moodEmoji}</Text>
                <Text style={styles.todayMoodText}>Feeling {moodLabel} today</Text>
              </View>
            </View>
            <View style={styles.streakBox}>
              <Text style={styles.streakLabel}>STREAK</Text>
              <Text style={styles.streakValue}>{streak}🔥</Text>
            </View>
          </View>
        </View>
 
        {/* Stats Cards */}
        <View style={styles.statsRow}>
          {/* Average Mood */}
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>AVG MOOD</Text>
            <Text style={styles.statValue}>{avgMoodData.emoji} {avgMoodData.label}</Text>
            <Text style={styles.statSub}>This week</Text>
          </View>
 
          {/* AI State */}
          <View style={styles.statCard}>
            <Text style={styles.statLabel}>AI STATE</Text>
            <Text style={[styles.statValue, { color: stateColor, fontSize: 15 }]}>
              {analysis?.mental_state || 'Normal'}
            </Text>
            <Text style={styles.statSub}>
              {Math.round((analysis?.confidence || 0) * 100)}% confidence
            </Text>
          </View>
        </View>
 
        {/* AI Cause Card */}
        {analysis?.cause && (
          <View style={styles.causeCard}>
            <Text style={styles.causeCardLabel}>🧠 AI DETECTED CAUSE</Text>
            <Text style={styles.causeCardValue}>{analysis.cause}</Text>
            <View style={styles.keywordsRow}>
              {analysis.keywords?.map((kw, i) => (
                <View key={i} style={styles.keywordChip}>
                  <Text style={styles.keywordText}>#{kw}</Text>
                </View>
              ))}
            </View>
          </View>
        )}
 
        {/* 7-Day Chart */}
        <View style={styles.chartCard}>
          <Text style={styles.chartTitle}>📈 7-Day Mood Trend</Text>
          {weekData.length > 0 ? (
            <MoodChart weekData={weekData} />
          ) : (
            <Text style={styles.noData}>No data yet — keep logging your mood!</Text>
          )}
        </View>
 
        {/* Risk Alert */}
        {riskAlert && (
          <View style={styles.riskAlert}>
            <Text style={styles.riskTitle}>⚠️ Mental Health Alert</Text>
            <Text style={styles.riskText}>
              Signs of <Text style={{ fontWeight: '800' }}>{riskState}</Text> detected recently.
              Consider reaching out to the campus counselor or a trusted person.
            </Text>
          </View>
        )}
 
        {/* Weekly Log */}
        <View style={styles.logCard}>
          <Text style={styles.logTitle}>📅 Weekly Log</Text>
          {weekData.map((day, i) => {
            const moodInfo = MOOD_LABELS[day.mood_level] || MOOD_LABELS[4];
            return (
              <View key={i} style={[styles.logRow, i < weekData.length - 1 && styles.logRowBorder]}>
                <Text style={styles.logDay}>{day.day}</Text>
                <Text style={{ fontSize: 20 }}>{moodInfo.emoji}</Text>
                <View style={styles.logBarBg}>
                  <View style={[styles.logBarFill, { width: `${(day.mood_level / 7) * 100}%`, backgroundColor: moodInfo.color }]} />
                </View>
                <Text style={[styles.logLabel, { color: moodInfo.color }]}>{moodInfo.label}</Text>
              </View>
            );
          })}
        </View>
 
        {/* New Session Button */}
        <TouchableOpacity
          style={styles.newSessionBtn}
          onPress={() => navigation.navigate('Mood')}
        >
          <Text style={styles.newSessionText}>+ Start New Session</Text>
        </TouchableOpacity>
 
        <Text style={styles.privacy}>🔒 Your data is private and confidential</Text>
 
      </ScrollView>
    </View>
  );
}
 
const styles = StyleSheet.create({
  container:         { flex: 1, backgroundColor: '#F8FAFB' },
  loadingContainer:  { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F8FAFB' },
  loadingText:       { marginTop: 12, fontSize: 14, color: '#9CA3AF' },
  header:            { backgroundColor: '#667eea', padding: 20, paddingTop: 52, paddingBottom: 36 },
  headerTop:         { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' },
  headerGreeting:    { color: 'rgba(255,255,255,0.75)', fontSize: 14, marginBottom: 4 },
  headerTitle:       { color: '#fff', fontSize: 24, fontWeight: '800', marginBottom: 12 },
  todayMoodBadge:    { flexDirection: 'row', alignItems: 'center', gap: 8, backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 20, paddingHorizontal: 14, paddingVertical: 6, alignSelf: 'flex-start' },
  todayMoodText:     { color: '#fff', fontSize: 13, fontWeight: '700' },
  streakBox:         { backgroundColor: 'rgba(255,255,255,0.2)', borderRadius: 16, padding: 14, alignItems: 'center' },
  streakLabel:       { color: 'rgba(255,255,255,0.7)', fontSize: 10, fontWeight: '600', marginBottom: 4 },
  streakValue:       { color: '#fff', fontSize: 28, fontWeight: '800' },
  statsRow:          { flexDirection: 'row', gap: 12, margin: 16, marginTop: -18 },
  statCard:          { flex: 1, backgroundColor: '#fff', borderRadius: 18, padding: 16, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.08, shadowRadius: 10, elevation: 5 },
  statLabel:         { fontSize: 9, color: '#9CA3AF', fontWeight: '700', letterSpacing: 1.2, textTransform: 'uppercase', marginBottom: 6 },
  statValue:         { fontSize: 16, fontWeight: '800', color: '#1a1a2e', marginBottom: 3 },
  statSub:           { fontSize: 10, color: '#9CA3AF' },
  causeCard:         { marginHorizontal: 16, marginBottom: 14, backgroundColor: '#EEF2FF', borderRadius: 16, padding: 16, borderWidth: 1, borderColor: '#C7D2FE' },
  causeCardLabel:    { fontSize: 10, fontWeight: '700', letterSpacing: 1.2, color: '#667eea', marginBottom: 6 },
  causeCardValue:    { fontSize: 16, fontWeight: '800', color: '#1a1a2e', marginBottom: 10 },
  keywordsRow:       { flexDirection: 'row', flexWrap: 'wrap', gap: 6 },
  keywordChip:       { backgroundColor: '#fff', borderRadius: 20, paddingHorizontal: 12, paddingVertical: 4 },
  keywordText:       { fontSize: 11, fontWeight: '700', color: '#667eea' },
  chartCard:         { marginHorizontal: 16, marginBottom: 14, backgroundColor: '#fff', borderRadius: 20, padding: 18, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.06, shadowRadius: 10, elevation: 4 },
  chartTitle:        { fontSize: 15, fontWeight: '800', color: '#1a1a2e', marginBottom: 16 },
  chartContainer:    { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end', height: 160 },
  chartBar:          { alignItems: 'center', flex: 1 },
  chartEmoji:        { fontSize: 14, marginBottom: 4 },
  chartBarBg:        { width: 24, height: 120, backgroundColor: '#F0F2F5', borderRadius: 12, justifyContent: 'flex-end', overflow: 'hidden' },
  chartBarFill:      { width: '100%', borderRadius: 12 },
  chartDay:          { fontSize: 10, color: '#9CA3AF', marginTop: 6, fontWeight: '600' },
  noData:            { textAlign: 'center', color: '#9CA3AF', fontSize: 13, padding: 20 },
  riskAlert:         { marginHorizontal: 16, marginBottom: 14, backgroundColor: '#FFFBEB', borderRadius: 16, padding: 16, borderWidth: 1.5, borderColor: '#FDE68A' },
  riskTitle:         { fontSize: 14, fontWeight: '800', color: '#92400E', marginBottom: 6 },
  riskText:          { fontSize: 13, color: '#B45309', lineHeight: 20 },
  logCard:           { marginHorizontal: 16, marginBottom: 14, backgroundColor: '#fff', borderRadius: 20, padding: 18, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.06, shadowRadius: 10, elevation: 4 },
  logTitle:          { fontSize: 15, fontWeight: '800', color: '#1a1a2e', marginBottom: 14 },
  logRow:            { flexDirection: 'row', alignItems: 'center', gap: 12, paddingVertical: 10 },
  logRowBorder:      { borderBottomWidth: 1, borderBottomColor: '#F0F2F5' },
  logDay:            { fontSize: 11, fontWeight: '700', color: '#9CA3AF', width: 30 },
  logBarBg:          { flex: 1, height: 6, backgroundColor: '#F0F2F5', borderRadius: 3, overflow: 'hidden' },
  logBarFill:        { height: '100%', borderRadius: 3 },
  logLabel:          { fontSize: 11, fontWeight: '700', width: 52, textAlign: 'right' },
  newSessionBtn:     { margin: 16, backgroundColor: '#667eea', borderRadius: 16, padding: 16, alignItems: 'center', shadowColor: '#667eea', shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.4, shadowRadius: 16, elevation: 8 },
  newSessionText:    { color: '#fff', fontSize: 16, fontWeight: '800' },
  privacy:           { textAlign: 'center', fontSize: 11, color: '#CBD5E1', marginBottom: 30 },
});