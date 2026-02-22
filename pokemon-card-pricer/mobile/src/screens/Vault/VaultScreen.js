import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Dimensions,
  Image,
  RefreshControl,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation } from '@react-navigation/native';
import { useVault } from '../../services/VaultService';

const { width } = Dimensions.get('window');
const cardWidth = (width - 60) / 2; // 2 cards per row with margins

export default function VaultScreen() {
  const navigation = useNavigation();
  const { cards, isLoading, refreshCards, getTotalValue, deleteCard } = useVault();
  const [sortBy, setSortBy] = useState('recent'); // recent, name, grade, value
  const [filterBy, setFilterBy] = useState('all'); // all, mint, excellent, good

  useEffect(() => {
    refreshCards();
  }, []);

  const getSortedAndFilteredCards = () => {
    let filteredCards = [...cards];

    // Apply filter
    if (filterBy !== 'all') {
      filteredCards = filteredCards.filter(card => {
        const grade = parseFloat(card.overallGrade);
        switch (filterBy) {
          case 'mint': return grade >= 9;
          case 'excellent': return grade >= 7 && grade < 9;
          case 'good': return grade < 7;
          default: return true;
        }
      });
    }

    // Apply sort
    filteredCards.sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'grade':
          return parseFloat(b.overallGrade) - parseFloat(a.overallGrade);
        case 'value':
          const aValue = parseFloat(a.marketValue?.replace('$', '') || 0);
          const bValue = parseFloat(b.marketValue?.replace('$', '') || 0);
          return bValue - aValue;
        case 'recent':
        default:
          return new Date(b.scannedAt) - new Date(a.scannedAt);
      }
    });

    return filteredCards;
  };

  const handleCardPress = (card) => {
    navigation.navigate('CardDetail', { 
      card,
      cardName: card.name 
    });
  };

  const handleDeleteCard = (card) => {
    Alert.alert(
      'Remove Card',
      `Are you sure you want to remove ${card.name} from your vault?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Remove',
          style: 'destructive',
          onPress: () => deleteCard(card.id)
        }
      ]
    );
  };

  const renderCard = ({ item: card }) => (
    <TouchableOpacity
      style={styles.cardContainer}
      onPress={() => handleCardPress(card)}
      onLongPress={() => handleDeleteCard(card)}
    >
      <LinearGradient
        colors={getGradeColors(card.overallGrade)}
        style={styles.cardGradient}
      >
        <View style={styles.cardContent}>
          {/* Card Image */}
          {card.photoUri ? (
            <Image 
              source={{ uri: card.photoUri }} 
              style={styles.cardImage}
              resizeMode="cover"
            />
          ) : (
            <View style={styles.cardImagePlaceholder}>
              <Icon name="image" size={40} color="#666" />
            </View>
          )}

          {/* Card Info */}
          <View style={styles.cardInfo}>
            <Text style={styles.cardName} numberOfLines={1}>
              {card.name}
            </Text>
            <Text style={styles.cardSet} numberOfLines={1}>
              {card.set}
            </Text>
            <Text style={styles.cardNumber}>
              #{card.setNumber}
            </Text>
          </View>

          {/* Grade Badge */}
          <View style={styles.gradeBadge}>
            <Text style={styles.gradeText}>
              {card.overallGrade}
            </Text>
          </View>

          {/* Value Badge */}
          {card.marketValue && (
            <View style={styles.valueBadge}>
              <Text style={styles.valueText}>
                {card.marketValue}
              </Text>
            </View>
          )}

          {/* Quality Indicator */}
          <View style={styles.qualityIndicator}>
            {[...Array(5)].map((_, i) => (
              <Icon
                key={i}
                name="star"
                size={12}
                color={i < Math.floor(parseFloat(card.overallGrade)) ? '#FFD700' : '#333'}
              />
            ))}
          </View>
        </View>
      </LinearGradient>
    </TouchableOpacity>
  );

  const renderHeader = () => (
    <View style={styles.header}>
      {/* Stats Summary */}
      <LinearGradient
        colors={['#1e3c72', '#2a5298']}
        style={styles.statsContainer}
      >
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{cards.length}</Text>
          <Text style={styles.statLabel}>Cards</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statValue}>${getTotalValue().toFixed(2)}</Text>
          <Text style={styles.statLabel}>Total Value</Text>
        </View>
        <View style={styles.statDivider} />
        <View style={styles.statItem}>
          <Text style={styles.statValue}>
            {cards.length > 0 ? 
              (cards.reduce((sum, card) => sum + parseFloat(card.overallGrade), 0) / cards.length).toFixed(1)
              : '0.0'
            }
          </Text>
          <Text style={styles.statLabel}>Avg Grade</Text>
        </View>
      </LinearGradient>

      {/* Filter and Sort Controls */}
      <View style={styles.controlsContainer}>
        {/* Sort Controls */}
        <View style={styles.sortContainer}>
          <Text style={styles.controlLabel}>Sort by:</Text>
          <View style={styles.sortButtons}>
            {[
              { key: 'recent', label: 'Recent' },
              { key: 'name', label: 'Name' },
              { key: 'grade', label: 'Grade' },
              { key: 'value', label: 'Value' }
            ].map(option => (
              <TouchableOpacity
                key={option.key}
                style={[
                  styles.sortButton,
                  sortBy === option.key && styles.sortButtonActive
                ]}
                onPress={() => setSortBy(option.key)}
              >
                <Text style={[
                  styles.sortButtonText,
                  sortBy === option.key && styles.sortButtonTextActive
                ]}>
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Filter Controls */}
        <View style={styles.filterContainer}>
          <Text style={styles.controlLabel}>Filter:</Text>
          <View style={styles.filterButtons}>
            {[
              { key: 'all', label: 'All', icon: 'apps' },
              { key: 'mint', label: 'Mint', icon: 'diamond' },
              { key: 'excellent', label: 'Excellent', icon: 'star' },
              { key: 'good', label: 'Good', icon: 'thumb-up' }
            ].map(option => (
              <TouchableOpacity
                key={option.key}
                style={[
                  styles.filterButton,
                  filterBy === option.key && styles.filterButtonActive
                ]}
                onPress={() => setFilterBy(option.key)}
              >
                <Icon 
                  name={option.icon} 
                  size={16} 
                  color={filterBy === option.key ? '#ffffff' : '#666'} 
                />
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>
    </View>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Icon name="folder-open" size={80} color="#666" />
      <Text style={styles.emptyTitle}>Your Vault is Empty</Text>
      <Text style={styles.emptyText}>
        Start scanning Pokemon cards to build your digital collection!
      </Text>
      <TouchableOpacity
        style={styles.scanButton}
        onPress={() => navigation.navigate('ScannerTab')}
      >
        <LinearGradient
          colors={['#4CAF50', '#45a049']}
          style={styles.scanButtonGradient}
        >
          <Icon name="camera-alt" size={20} color="#ffffff" />
          <Text style={styles.scanButtonText}>Scan First Card</Text>
        </LinearGradient>
      </TouchableOpacity>
    </View>
  );

  const getGradeColors = (grade) => {
    const gradeNum = parseFloat(grade);
    if (gradeNum >= 9) return ['#4CAF50', '#2E7D32'];
    if (gradeNum >= 8) return ['#8BC34A', '#558B2F'];
    if (gradeNum >= 7) return ['#FFC107', '#F57F17'];
    if (gradeNum >= 6) return ['#FF9800', '#E65100'];
    return ['#F44336', '#C62828'];
  };

  const sortedCards = getSortedAndFilteredCards();

  return (
    <SafeAreaView style={styles.container}>
      {cards.length === 0 && !isLoading ? (
        renderEmptyState()
      ) : (
        <FlatList
          data={sortedCards}
          renderItem={renderCard}
          keyExtractor={item => item.id}
          numColumns={2}
          ListHeaderComponent={renderHeader}
          contentContainerStyle={styles.listContainer}
          columnWrapperStyle={styles.row}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl
              refreshing={isLoading}
              onRefresh={refreshCards}
              tintColor="#4CAF50"
            />
          }
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  listContainer: {
    padding: 20,
  },
  row: {
    justifyContent: 'space-between',
  },
  header: {
    marginBottom: 20,
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 20,
    borderRadius: 15,
    marginBottom: 20,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
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
  statDivider: {
    width: 1,
    backgroundColor: 'rgba(255,255,255,0.2)',
    marginHorizontal: 15,
  },
  controlsContainer: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 15,
  },
  sortContainer: {
    marginBottom: 15,
  },
  controlLabel: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  sortButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  sortButton: {
    backgroundColor: '#333',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 15,
    marginRight: 8,
    marginBottom: 8,
  },
  sortButtonActive: {
    backgroundColor: '#4CAF50',
  },
  sortButtonText: {
    color: '#ffffff',
    fontSize: 12,
  },
  sortButtonTextActive: {
    fontWeight: 'bold',
  },
  filterContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  filterButtons: {
    flexDirection: 'row',
    flex: 1,
    justifyContent: 'space-around',
  },
  filterButton: {
    backgroundColor: '#333',
    padding: 8,
    borderRadius: 20,
    width: 36,
    height: 36,
    justifyContent: 'center',
    alignItems: 'center',
  },
  filterButtonActive: {
    backgroundColor: '#4CAF50',
  },
  cardContainer: {
    width: cardWidth,
    marginBottom: 20,
    borderRadius: 12,
    overflow: 'hidden',
  },
  cardGradient: {
    padding: 2,
  },
  cardContent: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    overflow: 'hidden',
  },
  cardImage: {
    width: '100%',
    height: cardWidth * 1.4, // Pokemon card aspect ratio
    backgroundColor: '#333',
  },
  cardImagePlaceholder: {
    width: '100%',
    height: cardWidth * 1.4,
    backgroundColor: '#333',
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardInfo: {
    padding: 10,
  },
  cardName: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  cardSet: {
    color: '#ffffff',
    fontSize: 12,
    opacity: 0.7,
    marginTop: 2,
  },
  cardNumber: {
    color: '#ffffff',
    fontSize: 11,
    opacity: 0.6,
    marginTop: 1,
  },
  gradeBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  gradeText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  valueBadge: {
    position: 'absolute',
    top: 8,
    left: 8,
    backgroundColor: 'rgba(76, 175, 80, 0.9)',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  valueText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  qualityIndicator: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    flexDirection: 'row',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyTitle: {
    color: '#ffffff',
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 20,
    marginBottom: 10,
  },
  emptyText: {
    color: '#ffffff',
    fontSize: 16,
    textAlign: 'center',
    opacity: 0.7,
    marginBottom: 30,
  },
  scanButton: {
    borderRadius: 25,
    overflow: 'hidden',
  },
  scanButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 12,
  },
  scanButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 8,
  },
});