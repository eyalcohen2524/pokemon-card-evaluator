import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { MaterialIcons as Icon } from '@expo/vector-icons';

// Screens
import ScannerScreen from './src/screens/Scanner/ScannerScreen';
import ScanResultScreen from './src/screens/Scanner/ScanResultScreen';
import VaultScreen from './src/screens/Vault/VaultScreen';
import CardDetailScreen from './src/screens/Vault/CardDetailScreen';
import MarketScreen from './src/screens/Market/MarketScreen';
import ProfileScreen from './src/screens/Profile/ProfileScreen';

// Services
import { VaultProvider } from './src/services/VaultService';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

// Scanner Stack
function ScannerStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen 
        name="Scanner" 
        component={ScannerScreen}
        options={{ headerShown: false }}
      />
      <Stack.Screen 
        name="ScanResult" 
        component={ScanResultScreen}
        options={{
          title: 'Grading Results',
          headerStyle: { backgroundColor: '#1a1a2e' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: 'bold' }
        }}
      />
    </Stack.Navigator>
  );
}

// Vault Stack
function VaultStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen 
        name="Vault" 
        component={VaultScreen}
        options={{
          title: 'My Vault',
          headerStyle: { backgroundColor: '#1a1a2e' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: 'bold' }
        }}
      />
      <Stack.Screen 
        name="CardDetail" 
        component={CardDetailScreen}
        options={({ route }) => ({
          title: route.params?.cardName || 'Card Details',
          headerStyle: { backgroundColor: '#1a1a2e' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: 'bold' }
        })}
      />
    </Stack.Navigator>
  );
}

// Main Tab Navigator
function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'ScannerTab') {
            iconName = 'camera-alt';
          } else if (route.name === 'VaultTab') {
            iconName = 'folder';
          } else if (route.name === 'Market') {
            iconName = 'trending-up';
          } else if (route.name === 'Profile') {
            iconName = 'person';
          }

          return <Icon name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#4CAF50',
        tabBarInactiveTintColor: 'gray',
        tabBarStyle: {
          backgroundColor: '#1a1a2e',
          borderTopColor: '#333',
        },
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="ScannerTab" 
        component={ScannerStack}
        options={{ title: 'Scan' }}
      />
      <Tab.Screen 
        name="VaultTab" 
        component={VaultStack}
        options={{ title: 'Vault' }}
      />
      <Tab.Screen 
        name="Market" 
        component={MarketScreen}
        options={{
          title: 'Market',
          headerShown: true,
          headerStyle: { backgroundColor: '#1a1a2e' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: 'bold' }
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Profile',
          headerShown: true,
          headerStyle: { backgroundColor: '#1a1a2e' },
          headerTintColor: '#ffffff',
          headerTitleStyle: { fontWeight: 'bold' }
        }}
      />
    </Tab.Navigator>
  );
}

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <VaultProvider>
          <NavigationContainer>
            <MainTabs />
            <StatusBar style="light" />
          </NavigationContainer>
        </VaultProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}