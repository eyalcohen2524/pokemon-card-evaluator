import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  Dimensions,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation } from '@react-navigation/native';

const { width } = Dimensions.get('window');

export default function MarketScreen() {
  const navigation = useNavigation();
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTimeframe, setSelectedTimeframe] = useState('7d'); // 1d, 7d, 30d, 90d
  
  // Mock market data - in real app, this would come from API
  const [marketData, setMarketData] = useState(generateMockMarketData());

  useEffect(() => {
    // Simulate periodic market updates
    const interval = setInterval(() => {
      setMarketData(generateMockMarketData());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setMarketData(generateMockMarketData());
    setRefreshing(false);
  };

  const handleCardPress = (card) => {
    Alert.alert(
      card.name,
      `Current Market Value: ${card.currentPrice}\nChange: ${card.changePercent}%`,
      [
        { text: 'View Details', onPress: () => {/* Navigate to card details */} },
        { text: 'Cancel', style: 'cancel' }
      ]
    );
  };

  const renderMarketSummary = () => (
    <View style={styles.summaryContainer}>
      <LinearGradient
        colors={['#1e3c72', '#2a5298']}
        style={styles.summaryGradient}
      >
        <Text style={styles.summaryTitle}>Market Overview</Text>
        
        <View style={styles.summaryStats}>
          <View style={styles.statItem}>
            <Text style={styles.statValue}>+12.4%</Text>
            <Text style={styles.statLabel}>Market Growth</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>1,247</Text>
            <Text style={styles.statLabel}>Active Listings</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Text style={styles.statValue}>$2.8M</Text>
            <Text style={styles.statLabel}>Volume (7d)</Text>
          </View>
        </View>

        <View style={styles.timeframeSelector}>
          {['1d', '7d', '30d', '90d'].map(timeframe => (
            <TouchableOpacity
              key={timeframe}
              style={[
                styles.timeframeButton,
                selectedTimeframe === timeframe && styles.timeframeButtonActive
              ]}
              onPress={() => setSelectedTimeframe(timeframe)}
            >
              <Text style={[
                styles.timeframeText,
                selectedTimeframe === timeframe && styles.timeframeTextActive
              ]}>
                {timeframe}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </LinearGradient>
    </View>
  );

  const renderMoversAndShakers = () => (
    <View style={styles.sectionContainer}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>🔥 Movers & Shakers</Text>
        <Text style={styles.sectionSubtitle}>Top price changes in the last {selectedTimeframe}</Text>
      </View>

      {marketData.movers.map((card, index) => (
        <TouchableOpacity
          key={card.id}
          style={styles.moverCard}
          onPress={() => handleCardPress(card)}
        >
          <LinearGradient
            colors={card.changePercent > 0 ? ['#4CAF50', '#2E7D32'] : ['#F44336', '#C62828']}
            style={styles.moverGradient}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
          >
            <View style={styles.moverContent}>
              <View style={styles.moverRank}>
                <Text style={styles.moverRankText}>#{index + 1}</Text>
              </View>

              <View style={styles.moverInfo}>
                <Text style={styles.moverName}>{card.name}</Text>
                <Text style={styles.moverSet}>{card.set}</Text>
                <Text style={styles.moverGrade}>{card.grade}</Text>
              </View>

              <View style={styles.moverPricing}>
                <Text style={styles.moverPrice}>{card.currentPrice}</Text>
                <View style={styles.moverChange}>
                  <Icon 
                    name={card.changePercent > 0 ? 'trending-up' : 'trending-down'} 
                    size={16} 
                    color="#ffffff" 
                  />
                  <Text style={styles.moverChangeText}>
                    {card.changePercent > 0 ? '+' : ''}{card.changePercent}%
                  </Text>
                </View>
              </View>
            </View>
          </LinearGradient>
        </TouchableOpacity>
      ))}
    </View>
  );

  const renderTrendingCards = () => (
    <View style={styles.sectionContainer}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>📈 Trending Now</Text>
        <Text style={styles.sectionSubtitle}>Most searched cards this week</Text>
      </View>

      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.trendingScrollContainer}
      >
        {marketData.trending.map((card, index) => (
          <TouchableOpacity
            key={card.id}
            style={styles.trendingCard}
            onPress={() => handleCardPress(card)}
          >
            <LinearGradient
              colors={['#16213e', '#1a1a2e']}
              style={styles.trendingGradient}
            >
              <View style={styles.trendingHeader}>
                <Text style={styles.trendingRank}>#{index + 1}</Text>
                <View style={styles.trendingBadge}>
                  <Icon name="whatshot" size={14} color="#FF5722" />
                </View>
              </View>

              <Text style={styles.trendingName}>{card.name}</Text>
              <Text style={styles.trendingSet}>{card.set}</Text>
              
              <View style={styles.trendingPrice}>
                <Text style={styles.trendingPriceText}>{card.currentPrice}</Text>
                <Text style={[
                  styles.trendingChange,
                  { color: card.changePercent > 0 ? '#4CAF50' : '#F44336' }
                ]}>
                  {card.changePercent > 0 ? '+' : ''}{card.changePercent}%
                </Text>
              </View>

              <View style={styles.trendingFooter}>
                <Icon name="search" size={12} color="#666" />
                <Text style={styles.trendingSearches}>
                  {card.searchVolume} searches
                </Text>
              </View>
            </LinearGradient>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );

  const renderNewsAndInsights = () => (
    <View style={styles.sectionContainer}>
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>📰 Market Insights</Text>
      </View>

      {marketData.insights.map((insight, index) => (
        <View key={index} style={styles.insightCard}>
          <LinearGradient
            colors={['#1a1a2e', '#16213e']}
            style={styles.insightGradient}
          >
            <View style={styles.insightHeader}>
              <Icon 
                name={insight.type === 'news' ? 'article' : 'lightbulb'} 
                size={20} 
                color="#4CAF50" 
              />
              <Text style={styles.insightType}>
                {insight.type === 'news' ? 'Market News' : 'Insight'}
              </Text>
              <Text style={styles.insightTime}>{insight.time}</Text>
            </View>

            <Text style={styles.insightTitle}>{insight.title}</Text>
            <Text style={styles.insightSummary}>{insight.summary}</Text>

            {insight.impact && (
              <View style={styles.insightImpact}>
                <Text style={styles.insightImpactLabel}>Market Impact:</Text>
                <Text style={[
                  styles.insightImpactValue,
                  { color: insight.impact.positive ? '#4CAF50' : '#F44336' }
                ]}>
                  {insight.impact.text}
                </Text>
              </View>
            )}
          </LinearGradient>
        </View>
      ))}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        style={styles.scrollView}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#4CAF50"
          />
        }
        showsVerticalScrollIndicator={false}
      >
        {renderMarketSummary()}
        {renderMoversAndShakers()}
        {renderTrendingCards()}
        {renderNewsAndInsights()}

        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Market data updates every 30 seconds
          </Text>
          <Text style={styles.footerTime}>
            Last updated: {new Date().toLocaleTimeString()}
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// Generate mock market data
function generateMockMarketData() {
  const cards = [
    'Charizard Base Set PSA 10',
    'Pikachu Illustrator PSA 9',
    'Blastoise Base Set BGS 9.5',
    'Venusaur Base Set PSA 9',
    'Alakazam Base Set PSA 8',
    'Gyarados Base Set PSA 10',
    'Mewtwo Base Set BGS 10',
    'Mew Ancient Mew PSA 10'
  ];

  const sets = ['Base Set', 'Jungle', 'Fossil', 'Team Rocket', 'Gym Heroes'];
  const grades = ['PSA 8', 'PSA 9', 'PSA 10', 'BGS 9.5', 'BGS 10'];

  const movers = cards.slice(0, 5).map((name, index) => ({
    id: `mover_${index}`,
    name: name.split(' ').slice(0, -2).join(' '),
    set: name.includes('Base Set') ? 'Base Set' : sets[Math.floor(Math.random() * sets.length)],
    grade: grades[Math.floor(Math.random() * grades.length)],
    currentPrice: `$${(Math.random() * 5000 + 500).toFixed(0)}`,
    changePercent: (Math.random() * 60 - 20).toFixed(1), // -20% to +40%
  }));

  const trending = cards.slice(2, 7).map((name, index) => ({
    id: `trending_${index}`,
    name: name.split(' ').slice(0, -2).join(' '),
    set: name.includes('Base Set') ? 'Base Set' : sets[Math.floor(Math.random() * sets.length)],
    currentPrice: `$${(Math.random() * 3000 + 200).toFixed(0)}`,
    changePercent: (Math.random() * 40 - 10).toFixed(1), // -10% to +30%
    searchVolume: Math.floor(Math.random() * 5000 + 1000),
  }));

  const insights = [
    {
      type: 'news',
      title: 'Pokemon TCG Market Reaches Record High',
      summary: 'Vintage Pokemon cards continue to break auction records as collector interest surges.',
      time: '2h ago',
      impact: { positive: true, text: 'Bullish for vintage cards' }
    },
    {
      type: 'insight',
      title: 'Base Set Holos Show Strong Performance',
      summary: 'PSA 10 Base Set holos have gained an average of 15% this month.',
      time: '1d ago',
      impact: { positive: true, text: '+15% average gain' }
    },
    {
      type: 'news',
      title: 'New Pokemon Set Release Impact',
      summary: 'Modern card prices may see short-term volatility with upcoming set release.',
      time: '3d ago',
      impact: { positive: false, text: 'Watch modern prices' }
    }
  ];

  return { movers, trending, insights };
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  scrollView: {
    flex: 1,
  },
  summaryContainer: {
    margin: 20,
    borderRadius: 15,
    overflow: 'hidden',
  },
  summaryGradient: {
    padding: 20,
  },
  summaryTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 15,
  },
  summaryStats: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
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
  timeframeSelector: {
    flexDirection: 'row',
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 20,
    padding: 4,
  },
  timeframeButton: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 16,
  },
  timeframeButtonActive: {
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  timeframeText: {
    color: '#ffffff',
    fontSize: 14,
    opacity: 0.7,
  },
  timeframeTextActive: {
    opacity: 1,
    fontWeight: 'bold',
  },
  sectionContainer: {
    marginHorizontal: 20,
    marginBottom: 25,
  },
  sectionHeader: {
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 5,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#ffffff',
    opacity: 0.7,
  },
  moverCard: {
    marginBottom: 10,
    borderRadius: 12,
    overflow: 'hidden',
  },
  moverGradient: {
    padding: 3,
  },
  moverContent: {
    backgroundColor: 'rgba(255,255,255,0.1)',
    padding: 15,
    borderRadius: 9,
    flexDirection: 'row',
    alignItems: 'center',
  },
  moverRank: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  moverRankText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  moverInfo: {
    flex: 1,
  },
  moverName: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  moverSet: {
    color: '#ffffff',
    fontSize: 13,
    opacity: 0.8,
    marginTop: 2,
  },
  moverGrade: {
    color: '#ffffff',
    fontSize: 12,
    opacity: 0.7,
    marginTop: 1,
  },
  moverPricing: {
    alignItems: 'flex-end',
  },
  moverPrice: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  moverChange: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 2,
  },
  moverChangeText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 4,
  },
  trendingScrollContainer: {
    paddingRight: 20,
  },
  trendingCard: {
    width: 150,
    marginRight: 15,
    borderRadius: 12,
    overflow: 'hidden',
  },
  trendingGradient: {
    padding: 15,
  },
  trendingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  trendingRank: {
    color: '#4CAF50',
    fontSize: 14,
    fontWeight: 'bold',
  },
  trendingBadge: {
    backgroundColor: 'rgba(255, 87, 34, 0.2)',
    padding: 4,
    borderRadius: 8,
  },
  trendingName: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  trendingSet: {
    color: '#ffffff',
    fontSize: 12,
    opacity: 0.7,
    marginBottom: 8,
  },
  trendingPrice: {
    marginBottom: 8,
  },
  trendingPriceText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  trendingChange: {
    fontSize: 12,
    fontWeight: 'bold',
    marginTop: 2,
  },
  trendingFooter: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trendingSearches: {
    color: '#666',
    fontSize: 11,
    marginLeft: 4,
  },
  insightCard: {
    marginBottom: 15,
    borderRadius: 12,
    overflow: 'hidden',
  },
  insightGradient: {
    padding: 15,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  insightType: {
    color: '#4CAF50',
    fontSize: 12,
    fontWeight: 'bold',
    marginLeft: 8,
    flex: 1,
  },
  insightTime: {
    color: '#666',
    fontSize: 11,
  },
  insightTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  insightSummary: {
    color: '#ffffff',
    fontSize: 14,
    opacity: 0.8,
    lineHeight: 20,
    marginBottom: 10,
  },
  insightImpact: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  insightImpactLabel: {
    color: '#666',
    fontSize: 12,
    marginRight: 8,
  },
  insightImpactValue: {
    fontSize: 12,
    fontWeight: 'bold',
  },
  footer: {
    alignItems: 'center',
    padding: 20,
    marginTop: 20,
  },
  footerText: {
    color: '#666',
    fontSize: 12,
    marginBottom: 5,
  },
  footerTime: {
    color: '#666',
    fontSize: 11,
  },
});