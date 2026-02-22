import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  Switch,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useVault } from '../../services/VaultService';

export default function ProfileScreen() {
  const { getCollectionStats, exportVault, clearVault } = useVault();
  
  // Settings state
  const [settings, setSettings] = useState({
    notifications: true,
    autoBackup: false,
    hapticFeedback: true,
    darkMode: true,
    priceAlerts: true,
  });

  const stats = getCollectionStats();

  const handleExportData = async () => {
    try {
      const exportData = exportVault();
      
      Alert.alert(
        'Export Data',
        'Your vault data has been prepared. In a real app, this would be saved to your device or shared.',
        [
          {
            text: 'View Sample',
            onPress: () => {
              const sampleData = JSON.parse(exportData);
              Alert.alert(
                'Export Preview',
                `Total Cards: ${sampleData.totalCards}\nExported At: ${new Date(sampleData.exportedAt).toLocaleString()}`
              );
            }
          },
          { text: 'OK', style: 'cancel' }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to export data. Please try again.');
    }
  };

  const handleClearVault = () => {
    Alert.alert(
      'Clear All Data',
      'Are you sure you want to delete all cards from your vault? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear All',
          style: 'destructive',
          onPress: async () => {
            try {
              await clearVault();
              Alert.alert('Success', 'Your vault has been cleared.');
            } catch (error) {
              Alert.alert('Error', 'Failed to clear vault. Please try again.');
            }
          }
        }
      ]
    );
  };

  const toggleSetting = (key) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const renderStats = () => (
    <View style={styles.statsContainer}>
      <LinearGradient
        colors={['#1e3c72', '#2a5298']}
        style={styles.statsGradient}
      >
        <Text style={styles.statsTitle}>Collection Stats</Text>
        
        <View style={styles.statsGrid}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{stats.totalCards}</Text>
            <Text style={styles.statLabel}>Total Cards</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>${stats.totalValue.toFixed(2)}</Text>
            <Text style={styles.statLabel}>Total Value</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>{stats.averageGrade}</Text>
            <Text style={styles.statLabel}>Avg Grade</Text>
          </View>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>
              {Object.keys(stats.setCounts).length}
            </Text>
            <Text style={styles.statLabel}>Different Sets</Text>
          </View>
        </View>
      </LinearGradient>
    </View>
  );

  const renderTopCards = () => (
    <View style={styles.sectionContainer}>
      <Text style={styles.sectionTitle}>🏆 Most Valuable Cards</Text>
      {stats.topCards.length > 0 ? (
        stats.topCards.map((card, index) => (
          <View key={card.id} style={styles.topCardItem}>
            <View style={styles.topCardRank}>
              <Text style={styles.topCardRankText}>#{index + 1}</Text>
            </View>
            <View style={styles.topCardInfo}>
              <Text style={styles.topCardName}>{card.name}</Text>
              <Text style={styles.topCardSet}>{card.set}</Text>
            </View>
            <View style={styles.topCardValue}>
              <Text style={styles.topCardValueText}>{card.marketValue}</Text>
              <Text style={styles.topCardGrade}>Grade: {card.overallGrade}</Text>
            </View>
          </View>
        ))
      ) : (
        <Text style={styles.emptyText}>No cards in vault yet</Text>
      )}
    </View>
  );

  const renderSettings = () => (
    <View style={styles.sectionContainer}>
      <Text style={styles.sectionTitle}>⚙️ Settings</Text>
      
      {Object.entries(settings).map(([key, value]) => (
        <View key={key} style={styles.settingItem}>
          <View style={styles.settingInfo}>
            <Text style={styles.settingLabel}>
              {getSettingLabel(key)}
            </Text>
            <Text style={styles.settingDescription}>
              {getSettingDescription(key)}
            </Text>
          </View>
          <Switch
            value={value}
            onValueChange={() => toggleSetting(key)}
            trackColor={{ false: '#333', true: '#4CAF50' }}
            thumbColor={value ? '#ffffff' : '#666'}
          />
        </View>
      ))}
    </View>
  );

  const renderActions = () => (
    <View style={styles.sectionContainer}>
      <Text style={styles.sectionTitle}>🔧 Data & Privacy</Text>
      
      <TouchableOpacity style={styles.actionButton} onPress={handleExportData}>
        <LinearGradient
          colors={['#4CAF50', '#45a049']}
          style={styles.actionGradient}
        >
          <Icon name="download" size={20} color="#ffffff" />
          <Text style={styles.actionText}>Export Vault Data</Text>
          <Icon name="chevron-right" size={20} color="#ffffff" />
        </LinearGradient>
      </TouchableOpacity>

      <TouchableOpacity style={styles.actionButton}>
        <View style={styles.actionGradientPlain}>
          <Icon name="backup" size={20} color="#666" />
          <Text style={[styles.actionText, { color: '#666' }]}>
            Backup to Cloud (Pro)
          </Text>
          <Icon name="chevron-right" size={20} color="#666" />
        </View>
      </TouchableOpacity>

      <TouchableOpacity style={styles.actionButton}>
        <View style={styles.actionGradientPlain}>
          <Icon name="share" size={20} color="#4CAF50" />
          <Text style={styles.actionText}>Share Collection</Text>
          <Icon name="chevron-right" size={20} color="#4CAF50" />
        </View>
      </TouchableOpacity>

      <TouchableOpacity 
        style={[styles.actionButton, styles.dangerButton]} 
        onPress={handleClearVault}
      >
        <View style={styles.actionGradientPlain}>
          <Icon name="delete-forever" size={20} color="#F44336" />
          <Text style={[styles.actionText, { color: '#F44336' }]}>
            Clear All Data
          </Text>
          <Icon name="chevron-right" size={20} color="#F44336" />
        </View>
      </TouchableOpacity>
    </View>
  );

  const renderAppInfo = () => (
    <View style={styles.sectionContainer}>
      <Text style={styles.sectionTitle}>📱 App Info</Text>
      
      <View style={styles.infoItem}>
        <Text style={styles.infoLabel}>Version</Text>
        <Text style={styles.infoValue}>1.0.0</Text>
      </View>
      
      <View style={styles.infoItem}>
        <Text style={styles.infoLabel}>Build</Text>
        <Text style={styles.infoValue}>2024.02.16</Text>
      </View>
      
      <View style={styles.infoItem}>
        <Text style={styles.infoLabel}>Backend</Text>
        <Text style={styles.infoValue}>Pokemon Card API v1.0</Text>
      </View>

      <TouchableOpacity style={styles.linkButton}>
        <Icon name="help" size={16} color="#4CAF50" />
        <Text style={styles.linkText}>Help & Support</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.linkButton}>
        <Icon name="privacy-tip" size={16} color="#4CAF50" />
        <Text style={styles.linkText}>Privacy Policy</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.linkButton}>
        <Icon name="description" size={16} color="#4CAF50" />
        <Text style={styles.linkText}>Terms of Service</Text>
      </TouchableOpacity>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        {renderStats()}
        {renderTopCards()}
        {renderSettings()}
        {renderActions()}
        {renderAppInfo()}
        
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Made with ❤️ for Pokemon card collectors
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function getSettingLabel(key) {
  const labels = {
    notifications: 'Notifications',
    autoBackup: 'Auto Backup',
    hapticFeedback: 'Haptic Feedback',
    darkMode: 'Dark Mode',
    priceAlerts: 'Price Alerts',
  };
  return labels[key] || key;
}

function getSettingDescription(key) {
  const descriptions = {
    notifications: 'Receive app notifications',
    autoBackup: 'Automatically backup your vault',
    hapticFeedback: 'Vibrate on interactions',
    darkMode: 'Use dark theme',
    priceAlerts: 'Notify when card values change',
  };
  return descriptions[key] || '';
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  scrollView: {
    flex: 1,
    padding: 20,
  },
  statsContainer: {
    marginBottom: 25,
    borderRadius: 15,
    overflow: 'hidden',
  },
  statsGradient: {
    padding: 20,
  },
  statsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 15,
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  statItem: {
    width: '50%',
    alignItems: 'center',
    marginBottom: 15,
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  statLabel: {
    fontSize: 12,
    color: '#ffffff',
    opacity: 0.8,
    marginTop: 2,
  },
  sectionContainer: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 15,
  },
  topCardItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  topCardRank: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#4CAF50',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  topCardRankText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  topCardInfo: {
    flex: 1,
  },
  topCardName: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  topCardSet: {
    color: '#ffffff',
    fontSize: 12,
    opacity: 0.7,
    marginTop: 2,
  },
  topCardValue: {
    alignItems: 'flex-end',
  },
  topCardValueText: {
    color: '#4CAF50',
    fontSize: 16,
    fontWeight: 'bold',
  },
  topCardGrade: {
    color: '#ffffff',
    fontSize: 12,
    opacity: 0.7,
    marginTop: 2,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  settingInfo: {
    flex: 1,
  },
  settingLabel: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  settingDescription: {
    color: '#ffffff',
    fontSize: 12,
    opacity: 0.7,
    marginTop: 2,
  },
  actionButton: {
    marginBottom: 10,
    borderRadius: 12,
    overflow: 'hidden',
  },
  dangerButton: {
    marginTop: 10,
  },
  actionGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
  },
  actionGradientPlain: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#333',
  },
  actionText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    flex: 1,
    marginLeft: 10,
  },
  infoItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  infoLabel: {
    color: '#ffffff',
    fontSize: 14,
    opacity: 0.7,
  },
  infoValue: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  linkButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    marginTop: 5,
  },
  linkText: {
    color: '#4CAF50',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 8,
  },
  emptyText: {
    color: '#666',
    fontSize: 14,
    fontStyle: 'italic',
    textAlign: 'center',
    padding: 20,
  },
  footer: {
    alignItems: 'center',
    padding: 20,
    marginTop: 20,
  },
  footerText: {
    color: '#666',
    fontSize: 12,
    textAlign: 'center',
  },
});