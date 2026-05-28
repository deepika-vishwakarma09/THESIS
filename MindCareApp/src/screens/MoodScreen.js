// src/screens/MoodScreen.js
import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, StatusBar, Alert } from 'react-native';
import { registerUser, loginUser, logMood } from '../services/api';

const MOODS = [
  { id: 1, label: 'Angry',   emoji: '😡', color: '#FF5E5E' },
  { id: 2, label: 'Anxious', emoji: '😰', color: '#FF9A3C' },
  { id: 3, label: 'Tired',   emoji: '😴', color: '#9B8ED8' },
  { id: 4, label: 'Okay',    emoji: '😐', color: '#4EADE0' },
  { id: 5, label: 'Joyful',  emoji: '😊', color: '#3DC88A' },
  { id: 6, label: 'Happy',   emoji: '😄', color: '#F5C518' },
  { id: 7, label: 'Excited', emoji: '🤩', color: '#4CAF50' },
];

const ensureLoggedIn = async () => {
  // Check if token already exists
  const existing = localStorage.getItem('token');
  if (existing) return true;

  // Try login first
  try {
    await loginUser('dipika2', 'test123');
    return true;
  } catch {
    // Try register
    try {
      await registerUser('dipika2', 'dipika2@test.com', 'test123');
      return true;
    } catch (e) {
      console.log('Auth failed:', e?.response?.data || e.message);
      return false;
    }
  }
};

export default function MoodScreen({ navigation }) {
  const [selectedMood, setSelectedMood] = useState(null);
  const [loading, setLoading] = useState(false);
  const selectedMoodData = MOODS.find(m => m.id === selectedMood);

  const handleNext = async () => {
    if (!selectedMood) {
      Alert.alert('Select Mood', 'Please select how you are feeling!');
      return;
    }
    const mood = MOODS.find(m => m.id === selectedMood);
    setLoading(true);
    try {
      const loggedIn = await ensureLoggedIn();
      if (loggedIn) {
        try { await logMood(selectedMood, `Feeling ${mood.label} today`); }
        catch (e) { console.log('Mood log error:', e?.response?.data || e.message); }
      }
    } finally {
      setLoading(false);
      navigation.navigate('Chat', {
        moodLevel: selectedMood,
        moodLabel: mood.label,
        moodEmoji: mood.emoji,
        moodColor: mood.color,
      });
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor="#F0F4FF" />
      <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scroll}>
        <View style={styles.header}>
          <View style={styles.logoBox}><Text style={styles.logoEmoji}>🧠</Text></View>
          <Text style={styles.appName}>MindCare AI</Text>
          <Text style={styles.title}>How are you feeling{'\n'}today?</Text>
          <Text style={styles.subtitle}>Select your current mood to begin</Text>
        </View>

        <View style={styles.grid}>
          {MOODS.map((mood) => {
            const isSelected = selectedMood === mood.id;
            return (
              <TouchableOpacity
                key={mood.id}
                style={[styles.moodCard, {
                  backgroundColor: isSelected ? mood.color : '#fff',
                  borderColor: isSelected ? mood.color : '#EEF0F5',
                }]}
                onPress={() => setSelectedMood(mood.id)}
                activeOpacity={0.8}
              >
                <Text style={styles.moodEmoji}>{mood.emoji}</Text>
                <Text style={[styles.moodLabel, { color: isSelected ? '#fff' : '#374151' }]}>
                  {mood.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {selectedMood && (
          <View style={styles.scaleCard}>
            <Text style={styles.scaleTitle}>MOOD LEVEL</Text>
            <View style={styles.scaleBar}>
              {MOODS.map(m => (
                <View key={m.id} style={[styles.scaleSegment, { backgroundColor: m.id <= selectedMood ? m.color : '#EEF0F5' }]} />
              ))}
            </View>
            <View style={styles.scaleLabels}>
              <Text style={styles.scaleLabel}>😡 Level 1</Text>
              <Text style={styles.scaleCurrent}>{selectedMoodData?.emoji} Level {selectedMood}</Text>
              <Text style={styles.scaleLabel}>Level 7 🤩</Text>
            </View>
          </View>
        )}

        <TouchableOpacity
          style={[styles.nextBtn, !selectedMood && styles.nextBtnDisabled]}
          onPress={handleNext}
          disabled={!selectedMood || loading}
          activeOpacity={0.85}
        >
          {loading ? <ActivityIndicator color="#fff" /> : (
            <Text style={styles.nextBtnText}>
              {selectedMood ? `Continue with ${selectedMoodData?.label} ${selectedMoodData?.emoji}` : 'Select a mood to continue'}
            </Text>
          )}
        </TouchableOpacity>
        <Text style={styles.privacy}>🔒 Your data is private and confidential</Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container:        { flex: 1, backgroundColor: '#F0F4FF' },
  scroll:           { padding: 20, paddingBottom: 40 },
  header:           { alignItems: 'center', marginBottom: 28, marginTop: 20 },
  logoBox:          { width: 60, height: 60, borderRadius: 18, backgroundColor: '#667eea', justifyContent: 'center', alignItems: 'center', marginBottom: 12 },
  logoEmoji:        { fontSize: 28 },
  appName:          { fontSize: 12, fontWeight: '700', letterSpacing: 2, color: '#9CA3AF', textTransform: 'uppercase', marginBottom: 8 },
  title:            { fontSize: 26, fontWeight: '800', color: '#1a1a2e', textAlign: 'center', lineHeight: 34, marginBottom: 6 },
  subtitle:         { fontSize: 14, color: '#9CA3AF', textAlign: 'center' },
  grid:             { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 20 },
  moodCard:         { width: '47%', flexDirection: 'row', alignItems: 'center', padding: 14, borderRadius: 16, borderWidth: 1.5, gap: 10 },
  moodEmoji:        { fontSize: 26 },
  moodLabel:        { fontSize: 15, fontWeight: '700' },
  scaleCard:        { backgroundColor: '#fff', borderRadius: 16, padding: 16, marginBottom: 20, borderWidth: 1, borderColor: '#EEF0F5' },
  scaleTitle:       { fontSize: 10, fontWeight: '700', letterSpacing: 1.5, color: '#9CA3AF', marginBottom: 10 },
  scaleBar:         { flexDirection: 'row', gap: 4, marginBottom: 8 },
  scaleSegment:     { flex: 1, height: 10, borderRadius: 5 },
  scaleLabels:      { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  scaleLabel:       { fontSize: 10, color: '#9CA3AF' },
  scaleCurrent:     { fontSize: 12, fontWeight: '700', color: '#667eea' },
  nextBtn:          { backgroundColor: '#667eea', borderRadius: 16, padding: 16, alignItems: 'center', marginBottom: 16 },
  nextBtnDisabled:  { backgroundColor: '#E5E7EB' },
  nextBtnText:      { color: '#fff', fontSize: 16, fontWeight: '800' },
  privacy:          { textAlign: 'center', fontSize: 11, color: '#CBD5E1' },
});