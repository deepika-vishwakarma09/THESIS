
// App.js
// ───────
// Main app entry point with navigation setup
 
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { ActivityIndicator, View } from 'react-native';
 
import { AuthProvider, useAuth } from './src/context/AuthContext';
 
// ── Screens ────────────────────────────────────────────────
import MoodScreen      from './src/screens/MoodScreen';
import ChatScreen      from './src/screens/ChatScreen';
import InsightsScreen  from './src/screens/InsightsScreen';
import DashboardScreen from './src/screens/DashboardScreen';
 
const Stack = createStackNavigator();
 
// ── Main Navigation ────────────────────────────────────────
function AppNavigator() {
  const { user, loading } = useAuth();
 
  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F0F4FF' }}>
        <ActivityIndicator size="large" color="#667eea" />
      </View>
    );
  }
 
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerShown: false,
          cardStyle: { backgroundColor: '#F0F4FF' },
        }}
      >
        {/* Always show mood screen first */}
        <Stack.Screen name="Mood"      component={MoodScreen} />
        <Stack.Screen name="Chat"      component={ChatScreen} />
        <Stack.Screen name="Insights"  component={InsightsScreen} />
        <Stack.Screen name="Dashboard" component={DashboardScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
 
// ── Root App ───────────────────────────────────────────────
export default function App() {
  return (
    <AuthProvider>
      <AppNavigator />
    </AuthProvider>
  );
}