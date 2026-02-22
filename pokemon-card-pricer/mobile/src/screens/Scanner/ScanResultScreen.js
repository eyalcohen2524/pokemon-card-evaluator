import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  Image,
  Animated,
  Alert
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import * as Haptics from 'expo-haptics';
import { useNavigation } from '@react-navigation/native';

import RadarChart from '../../components/RadarChart';
import GradeReveal from '../../components/GradeReveal';
import { useVault } from '../../services/VaultService';

const { width } = Dimensions.get('window');

export default function ScanResultScreen({ route }) {
  const { scanResult, photoUri } = route.params;
  const navigation = useNavigation();
  const { addCard } = useVault();
  
  const [showReveal, setShowReveal] = useState(true);
  const [savedToVault, setSavedToVault] = useState(false);
  
  // Animations
  const slideUpAnim = useRef(new Animated.Value(300)).current;
  const fadeInAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Start entrance animation after reveal
    const timer = setTimeout(() => {
      Animated.parallel([
        Animated.timing(slideUpAnim, {
          toValue: 0,
          duration: 600,
          useNativeDriver: true,
        }),
        Animated.timing(fadeInAnim, {
          toValue: 1,
          duration: 600,
          useNativeDriver: true,
        }),
      ]).start();
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  const handleRevealComplete = () => {
    setShowReveal(false);
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
  };

  const handleSaveToVault = async () => {
    try {
      const cardData = {
        id: Date.now().toString(),
        name: scanResult.identified_info.name,
        set: scanResult.matches[0]?.card?.set_name || 'Unknown Set',
        setNumber: scanResult.identified_info.set_number,
        overallGrade: calculateOverallGrade(scanResult.grading),
        subgrades: scanResult.grading,
        marketValue: getMarketValue(scanResult.matches[0]?.pricing),
        photoUri: photoUri,
        scannedAt: new Date().toISOString(),
        confidence: scanResult.cv_confidence
      };

      await addCard(cardData);
      setSavedToVault(true);
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      
      Alert.alert(
        'Saved to Vault! 🎯',
        `${cardData.name} has been added to your digital vault.`,
        [
          { 
            text: 'View Vault', 
            onPress: () => navigation.navigate('VaultTab')
          },
          { text: 'Scan Another', style: 'cancel' }
        ]
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to save card to vault. Please try again.');
    }
  };

  const calculateOverallGrade = (grading) => {
    if (!grading) return 'N/A';
    const grades = Object.values(grading);
    const avg = grades.reduce((sum, grade) => sum + grade, 0) / grades.length;
    return Math.round(avg * 10) / 10;
  };

  const getMarketValue = (pricing) => {
    if (!pricing?.prices_by_grade) return 'N/A';
    
    const ungraded = pricing.prices_by_grade.Ungraded;
    if (ungraded?.avg_price) {
      return `$${ungraded.avg_price.toFixed(2)}`;
    }
    
    return 'N/A';
  };

  const getGradeColor = (grade) => {
    if (grade >= 9) return '#4CAF50'; // Green
    if (grade >= 8) return '#FF9800'; // Orange
    if (grade >= 7) return '#FF5722'; // Red-Orange
    return '#F44336'; // Red
  };

  if (showReveal) {
    return (
      <GradeReveal
        grade={calculateOverallGrade(scanResult.grading)}
        cardName={scanResult.identified_info.name}
        onComplete={handleRevealComplete}
      />
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <Animated.View
          style={[
            styles.content,
            {
              transform: [{ translateY: slideUpAnim }],
              opacity: fadeInAnim,
            }
          ]}
        >
          {/* Card Header */}
          <View style={styles.cardHeader}>
            <LinearGradient
              colors={['#1e3c72', '#2a5298']}
              style={styles.headerGradient}
            >
              <View style={styles.cardInfo}>
                <Text style={styles.cardName}>
                  {scanResult.identified_info.name}
                </Text>
                <Text style={styles.cardSet}>
                  {scanResult.matches[0]?.card?.set_name || 'Unknown Set'}
                </Text>
                <Text style={styles.cardNumber}>
                  #{scanResult.identified_info.set_number}
                </Text>
              </View>
              
              <View style={styles.confidenceContainer}>
                <Text style={styles.confidenceLabel}>Confidence</Text>
                <Text style={styles.confidenceValue}>
                  {Math.round(scanResult.cv_confidence * 100)}%
                </Text>
              </View>
            </LinearGradient>
          </View>

          {/* Overall Grade */}
          <View style={styles.gradeContainer}>
            <LinearGradient
              colors={[
                getGradeColor(calculateOverallGrade(scanResult.grading)),
                '#333'
              ]}
              style={styles.gradeCard}
            >
              <Text style={styles.gradeLabel}>Overall Grade</Text>
              <Text style={styles.gradeValue}>
                {calculateOverallGrade(scanResult.grading)}
              </Text>
              <View style={styles.gradeStars}>
                {[...Array(5)].map((_, i) => (
                  <Icon
                    key={i}
                    name="star"
                    size={24}
                    color={i < Math.floor(calculateOverallGrade(scanResult.grading)) 
                      ? '#FFD700' 
                      : '#666'
                    }
                  />
                ))}
              </View>
            </LinearGradient>
          </View>

          {/* Radar Chart */}
          {scanResult.grading && (
            <View style={styles.chartContainer}>
              <Text style={styles.sectionTitle}>Condition Breakdown</Text>
              <RadarChart
                data={scanResult.grading}
                size={width - 40}
                maxValue={10}
              />
            </View>
          )}

          {/* Sub-grades */}
          <View style={styles.subgradesContainer}>
            <Text style={styles.sectionTitle}>Sub-grades</Text>
            {scanResult.grading && Object.entries(scanResult.grading).map(([key, value]) => (
              <View key={key} style={styles.subgradeRow}>
                <Text style={styles.subgradeLabel}>
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                </Text>
                <View style={styles.subgradeBar}>
                  <LinearGradient
                    colors={[getGradeColor(value), '#333']}
                    style={[
                      styles.subgradeProgress,
                      { width: `${(value / 10) * 100}%` }
                    ]}
                  />
                </View>
                <Text style={[styles.subgradeValue, { color: getGradeColor(value) }]}>
                  {value}
                </Text>
              </View>
            ))}
          </View>

          {/* Market Value */}
          {scanResult.matches && scanResult.matches[0]?.pricing && (
            <View style={styles.valueContainer}>
              <Text style={styles.sectionTitle}>Estimated Market Value</Text>
              <LinearGradient
                colors={['#4CAF50', '#45a049']}
                style={styles.valueCard}
              >
                <Icon name="attach-money" size={32} color="#ffffff" />
                <Text style={styles.valueAmount}>
                  {getMarketValue(scanResult.matches[0].pricing)}
                </Text>
                <Text style={styles.valueNote}>
                  Based on recent sales (Ungraded)
                </Text>
              </LinearGradient>
            </View>
          )}

          {/* Action Buttons */}
          <View style={styles.actionsContainer}>
            <TouchableOpacity
              style={[
                styles.actionButton,
                savedToVault && styles.actionButtonDisabled
              ]}
              onPress={handleSaveToVault}
              disabled={savedToVault}
            >
              <LinearGradient
                colors={savedToVault ? ['#666', '#444'] : ['#4CAF50', '#45a049']}
                style={styles.actionButtonGradient}
              >
                <Icon 
                  name={savedToVault ? 'check' : 'save'} 
                  size={20} 
                  color="#ffffff" 
                />
                <Text style={styles.actionButtonText}>
                  {savedToVault ? 'Saved to Vault!' : 'Save to Vault'}
                </Text>
              </LinearGradient>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Scanner')}
            >
              <LinearGradient
                colors={['#2196F3', '#1976D2']}
                style={styles.actionButtonGradient}
              >
                <Icon name="camera-alt" size={20} color="#ffffff" />
                <Text style={styles.actionButtonText}>
                  Scan Another Card
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  scrollView: {
    flex: 1,
  },
  content: {
    padding: 20,
  },
  cardHeader: {
    marginBottom: 20,
    borderRadius: 15,
    overflow: 'hidden',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  headerGradient: {
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardInfo: {
    flex: 1,
  },
  cardName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 5,
  },
  cardSet: {
    fontSize: 16,
    color: '#ffffff',
    opacity: 0.8,
    marginBottom: 2,
  },
  cardNumber: {
    fontSize: 14,
    color: '#ffffff',
    opacity: 0.7,
  },
  confidenceContainer: {
    alignItems: 'center',
  },
  confidenceLabel: {
    fontSize: 12,
    color: '#ffffff',
    opacity: 0.8,
  },
  confidenceValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  gradeContainer: {
    marginBottom: 25,
    borderRadius: 15,
    overflow: 'hidden',
  },
  gradeCard: {
    padding: 25,
    alignItems: 'center',
  },
  gradeLabel: {
    fontSize: 16,
    color: '#ffffff',
    marginBottom: 10,
    opacity: 0.9,
  },
  gradeValue: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 10,
    textShadowColor: 'rgba(0,0,0,0.3)',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 4,
  },
  gradeStars: {
    flexDirection: 'row',
  },
  chartContainer: {
    marginBottom: 25,
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 20,
    alignItems: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 15,
    textAlign: 'center',
  },
  subgradesContainer: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 20,
    marginBottom: 25,
  },
  subgradeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 15,
  },
  subgradeLabel: {
    fontSize: 16,
    color: '#ffffff',
    width: 100,
  },
  subgradeBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#333',
    borderRadius: 4,
    marginHorizontal: 15,
  },
  subgradeProgress: {
    height: 8,
    borderRadius: 4,
  },
  subgradeValue: {
    fontSize: 16,
    fontWeight: 'bold',
    width: 30,
    textAlign: 'right',
  },
  valueContainer: {
    marginBottom: 25,
    borderRadius: 15,
    overflow: 'hidden',
  },
  valueCard: {
    padding: 20,
    alignItems: 'center',
  },
  valueAmount: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#ffffff',
    marginVertical: 5,
  },
  valueNote: {
    fontSize: 14,
    color: '#ffffff',
    opacity: 0.8,
  },
  actionsContainer: {
    marginTop: 20,
  },
  actionButton: {
    marginBottom: 15,
    borderRadius: 12,
    overflow: 'hidden',
  },
  actionButtonDisabled: {
    opacity: 0.7,
  },
  actionButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});