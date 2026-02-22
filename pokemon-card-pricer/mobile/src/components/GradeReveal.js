import React, { useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Animated,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import * as Haptics from 'expo-haptics';
import Icon from 'react-native-vector-icons/MaterialIcons';

const { width, height } = Dimensions.get('window');

export default function GradeReveal({ grade, cardName, onComplete }) {
  // Animation values
  const scaleAnim = useRef(new Animated.Value(0)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;
  const textOpacityAnim = useRef(new Animated.Value(0)).current;
  const sparkleAnimations = useRef([...Array(8)].map(() => ({
    scale: new Animated.Value(0),
    translateY: new Animated.Value(0),
    rotate: new Animated.Value(0),
  }))).current;

  useEffect(() => {
    // Start the reveal sequence
    startRevealSequence();
  }, []);

  const startRevealSequence = () => {
    // Phase 1: Initial scale up with haptic
    Animated.sequence([
      // Build up anticipation
      Animated.timing(scaleAnim, {
        toValue: 0.3,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.timing(scaleAnim, {
        toValue: 0.1,
        duration: 200,
        useNativeDriver: true,
      }),
      
      // The reveal!
      Animated.parallel([
        Animated.spring(scaleAnim, {
          toValue: 1,
          friction: 4,
          tension: 100,
          useNativeDriver: true,
        }),
        Animated.timing(textOpacityAnim, {
          toValue: 1,
          duration: 500,
          delay: 200,
          useNativeDriver: true,
        }),
      ])
    ]).start();

    // Phase 2: Glow effect
    setTimeout(() => {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      
      Animated.loop(
        Animated.sequence([
          Animated.timing(glowAnim, {
            toValue: 1,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(glowAnim, {
            toValue: 0,
            duration: 800,
            useNativeDriver: true,
          }),
        ])
      ).start();
    }, 500);

    // Phase 3: Sparkles
    setTimeout(() => {
      startSparkleAnimations();
    }, 800);

    // Phase 4: Complete
    setTimeout(() => {
      if (onComplete) {
        onComplete();
      }
    }, 3500);
  };

  const startSparkleAnimations = () => {
    sparkleAnimations.forEach((sparkle, index) => {
      const delay = index * 100;
      
      Animated.parallel([
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(sparkle.scale, {
            toValue: 1,
            duration: 300,
            useNativeDriver: true,
          }),
          Animated.timing(sparkle.scale, {
            toValue: 0,
            duration: 500,
            useNativeDriver: true,
          }),
        ]),
        Animated.sequence([
          Animated.delay(delay),
          Animated.timing(sparkle.translateY, {
            toValue: -50 - (index * 20),
            duration: 800,
            useNativeDriver: true,
          }),
        ]),
        Animated.loop(
          Animated.timing(sparkle.rotate, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          })
        ),
      ]).start();
    });
  };

  const getGradeColor = () => {
    const gradeNum = parseFloat(grade);
    if (gradeNum >= 9) return '#4CAF50';
    if (gradeNum >= 8) return '#8BC34A';
    if (gradeNum >= 7) return '#FFC107';
    if (gradeNum >= 6) return '#FF9800';
    return '#F44336';
  };

  const getGradeTitle = () => {
    const gradeNum = parseFloat(grade);
    if (gradeNum >= 9.5) return 'PRISTINE!';
    if (gradeNum >= 9) return 'MINT!';
    if (gradeNum >= 8) return 'EXCELLENT!';
    if (gradeNum >= 7) return 'VERY GOOD!';
    if (gradeNum >= 6) return 'GOOD';
    return 'FAIR';
  };

  const sparklePositions = [
    { left: '20%', top: '30%' },
    { right: '25%', top: '25%' },
    { left: '15%', top: '50%' },
    { right: '20%', top: '45%' },
    { left: '30%', top: '70%' },
    { right: '30%', top: '65%' },
    { left: '25%', bottom: '30%' },
    { right: '15%', bottom: '35%' },
  ];

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#0f0f23', '#1a1a2e', '#16213e']}
        style={styles.background}
      >
        {/* Sparkles */}
        {sparkleAnimations.map((sparkle, index) => (
          <Animated.View
            key={index}
            style={[
              styles.sparkle,
              sparklePositions[index],
              {
                transform: [
                  { scale: sparkle.scale },
                  { translateY: sparkle.translateY },
                  {
                    rotate: sparkle.rotate.interpolate({
                      inputRange: [0, 1],
                      outputRange: ['0deg', '360deg'],
                    }),
                  },
                ],
              },
            ]}
          >
            <Icon name="star" size={20} color="#FFD700" />
          </Animated.View>
        ))}

        {/* Main Content */}
        <Animated.View
          style={[
            styles.content,
            {
              transform: [{ scale: scaleAnim }],
            },
          ]}
        >
          {/* Glow Effect */}
          <Animated.View
            style={[
              styles.glowContainer,
              {
                opacity: glowAnim,
              },
            ]}
          >
            <LinearGradient
              colors={[
                'transparent',
                `${getGradeColor()}30`,
                `${getGradeColor()}60`,
                `${getGradeColor()}30`,
                'transparent',
              ]}
              style={styles.glow}
            />
          </Animated.View>

          {/* Grade Circle */}
          <View style={styles.gradeCircle}>
            <LinearGradient
              colors={[getGradeColor(), '#333']}
              style={styles.gradeCircleInner}
            >
              <Text style={styles.gradeNumber}>{grade}</Text>
            </LinearGradient>
          </View>

          {/* Card Info */}
          <Animated.View
            style={[
              styles.cardInfoContainer,
              {
                opacity: textOpacityAnim,
              },
            ]}
          >
            <Text style={styles.gradeTitle}>{getGradeTitle()}</Text>
            <Text style={styles.cardName}>{cardName}</Text>
            
            {/* Grade Description */}
            <View style={styles.gradeDescriptionContainer}>
              <Text style={[styles.gradeDescription, { color: getGradeColor() }]}>
                {getGradeDescription(parseFloat(grade))}
              </Text>
            </View>
          </Animated.View>

          {/* Loading Indicator */}
          <View style={styles.loadingContainer}>
            <Text style={styles.loadingText}>
              Analyzing card condition...
            </Text>
            <View style={styles.progressBar}>
              <Animated.View
                style={[
                  styles.progress,
                  {
                    width: scaleAnim.interpolate({
                      inputRange: [0, 1],
                      outputRange: ['0%', '100%'],
                    }),
                  },
                ]}
              />
            </View>
          </View>
        </Animated.View>

        {/* Floating Icons */}
        <View style={styles.floatingIcons}>
          <Icon name="verified" size={30} color="#4CAF50" style={styles.floatingIcon} />
          <Icon name="diamond" size={25} color="#FFD700" style={[styles.floatingIcon, { right: 50 }]} />
          <Icon name="workspace-premium" size={28} color="#9C27B0" style={[styles.floatingIcon, { left: 40, bottom: 100 }]} />
        </View>
      </LinearGradient>
    </View>
  );
}

function getGradeDescription(grade) {
  if (grade >= 9.5) return 'Virtually perfect condition';
  if (grade >= 9) return 'Near perfect condition';
  if (grade >= 8) return 'Excellent condition with minor flaws';
  if (grade >= 7) return 'Very good condition';
  if (grade >= 6) return 'Good condition with visible wear';
  return 'Fair condition with significant wear';
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  background: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  glowContainer: {
    position: 'absolute',
    width: width,
    height: height,
    justifyContent: 'center',
    alignItems: 'center',
  },
  glow: {
    width: 300,
    height: 300,
    borderRadius: 150,
  },
  gradeCircle: {
    width: 200,
    height: 200,
    borderRadius: 100,
    padding: 8,
    backgroundColor: '#ffffff',
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 5 },
    shadowOpacity: 0.3,
    shadowRadius: 10,
  },
  gradeCircleInner: {
    flex: 1,
    borderRadius: 100,
    justifyContent: 'center',
    alignItems: 'center',
  },
  gradeNumber: {
    fontSize: 72,
    fontWeight: 'bold',
    color: '#ffffff',
    textShadowColor: 'rgba(0,0,0,0.3)',
    textShadowOffset: { width: 2, height: 2 },
    textShadowRadius: 4,
  },
  cardInfoContainer: {
    marginTop: 40,
    alignItems: 'center',
  },
  gradeTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 10,
    textShadowColor: 'rgba(0,0,0,0.5)',
    textShadowOffset: { width: 1, height: 1 },
    textShadowRadius: 3,
  },
  cardName: {
    fontSize: 24,
    color: '#ffffff',
    opacity: 0.9,
    textAlign: 'center',
    marginBottom: 15,
  },
  gradeDescriptionContainer: {
    backgroundColor: 'rgba(0,0,0,0.3)',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  gradeDescription: {
    fontSize: 16,
    textAlign: 'center',
    fontWeight: '600',
  },
  loadingContainer: {
    position: 'absolute',
    bottom: -150,
    alignItems: 'center',
    width: width * 0.8,
  },
  loadingText: {
    color: '#ffffff',
    fontSize: 16,
    marginBottom: 10,
    opacity: 0.8,
  },
  progressBar: {
    width: '100%',
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 2,
  },
  progress: {
    height: 4,
    backgroundColor: '#4CAF50',
    borderRadius: 2,
  },
  sparkle: {
    position: 'absolute',
  },
  floatingIcons: {
    position: 'absolute',
    width: '100%',
    height: '100%',
  },
  floatingIcon: {
    position: 'absolute',
    opacity: 0.6,
  },
});