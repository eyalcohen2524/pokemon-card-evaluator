import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Animated,
  Dimensions,
  Alert,
  ActivityIndicator
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useNavigation } from '@react-navigation/native';
import { MaterialIcons as Icon } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { scanCard } from '../../services/CardScanService';

const { width, height } = Dimensions.get('window');

export default function ScannerScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const [facing, setFacing] = useState('back');
  const [isScanning, setIsScanning] = useState(false);
  const [flashMode, setFlashMode] = useState('off');
  const cameraRef = useRef(null);
  const navigation = useNavigation();
  
  // Animations
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const overlayOpacity = useRef(new Animated.Value(0.2)).current;

  useEffect(() => {
    // Permissions are now handled by useCameraPermissions hook

    // Start pulse animation
    const startPulseAnimation = () => {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 1500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: true,
          }),
        ]),
      ).start();
    };

    startPulseAnimation();
  }, []);

  const handleCapture = async () => {
    if (!cameraRef.current || isScanning) return;

    try {
      setIsScanning(true);
      
      // Haptic feedback
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

      // Animate overlay for scanning effect
      Animated.timing(overlayOpacity, {
        toValue: 0.3,
        duration: 200,
        useNativeDriver: true,
      }).start();

      // Debug camera ref
      console.log('Camera ref:', cameraRef.current);
      console.log('Available methods:', Object.getOwnPropertyNames(cameraRef.current));

      // Take photo - try different approaches for SDK 54
      let photo;
      try {
        photo = await cameraRef.current.takePictureAsync({
          quality: 0.8,
          base64: false,
          exif: false,
        });
      } catch (photoError) {
        console.log('First photo method failed, trying simpler approach:', photoError);
        photo = await cameraRef.current.takePictureAsync();
      }

      console.log('Photo taken successfully:', photo);

      // Call our backend API to identify the card
      const result = await scanCard(photo.uri);

      if (result.success) {
        // Navigate to results screen
        navigation.navigate('ScanResult', { 
          scanResult: result,
          photoUri: photo.uri 
        });
      } else {
        Alert.alert(
          'Scan Failed',
          result.error || 'Unable to identify card. Please try again with better lighting.',
          [{ text: 'OK' }]
        );
      }

    } catch (error) {
      console.error('Scanning error:', error);
      Alert.alert(
        'Error',
        'Failed to process image. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsScanning(false);
      
      // Reset overlay
      Animated.timing(overlayOpacity, {
        toValue: 0.7,
        duration: 200,
        useNativeDriver: true,
      }).start();
    }
  };

  const toggleFlash = () => {
    setFlashMode(
      flashMode === 'off'
        ? 'on'
        : 'off'
    );
    Haptics.selectionAsync();
  };

  const handleRequestPermission = async () => {
    try {
      const result = await requestPermission();
      if (result.granted) {
        // Permission granted, the component will re-render automatically
        console.log('Camera permission granted');
      } else {
        Alert.alert(
          'Permission Required',
          'Camera access is required to scan Pokemon cards. Please grant permission in Settings.',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      console.error('Error requesting camera permission:', error);
      Alert.alert(
        'Error',
        'Failed to request camera permission. Please check Settings manually.',
        [{ text: 'OK' }]
      );
    }
  };

  if (!permission) {
    return <View style={styles.container} />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.permissionContainer}>
        <Icon name="camera-alt" size={80} color="#666" />
        <Text style={styles.permissionText}>
          Camera permission is required to scan cards
        </Text>
        <TouchableOpacity
          style={styles.permissionButton}
          onPress={handleRequestPermission}
        >
          <Text style={styles.permissionButtonText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <CameraView
        style={styles.camera}
        facing={facing}
        flash={flashMode}
        ref={cameraRef}
      >
        {/* Top Controls */}
        <View style={styles.topControls}>
          <TouchableOpacity
            style={styles.controlButton}
            onPress={toggleFlash}
          >
            <Icon
              name={flashMode === 'off' ? 'flash-off' : 'flash-on'}
              size={24}
              color="#ffffff"
            />
          </TouchableOpacity>
        </View>

        {/* Card Scanning Overlay */}
        <View style={styles.overlayContainer}>
          <Animated.View
            style={[
              styles.overlay,
              { opacity: overlayOpacity }
            ]}
          />
          
          {/* Card Frame - Transparent */}
          <Animated.View
            style={[
              styles.cardFrame,
              { transform: [{ scale: pulseAnim }] }
            ]}
          >
            {/* Just the border outline - completely transparent inside */}
            <View style={styles.cardFrameContent}>
              {/* Corner guides */}
              <View style={styles.cornerGuide} />
              <View style={[styles.cornerGuide, styles.topRight]} />
              <View style={[styles.cornerGuide, styles.bottomLeft]} />
              <View style={[styles.cornerGuide, styles.bottomRight]} />
            </View>
          </Animated.View>
          
          {/* Instructions moved outside frame */}
          <View style={styles.frameInstructions}>
            <Text style={styles.frameText}>
              Position card within frame
            </Text>
            <Text style={styles.frameSubtext}>
              Ensure card is flat and well-lit
            </Text>
          </View>
        </View>

        {/* Bottom Controls */}
        <View style={styles.bottomControls}>
          <View style={styles.captureContainer}>
            <TouchableOpacity
              style={[
                styles.captureButton,
                isScanning && styles.captureButtonDisabled
              ]}
              onPress={handleCapture}
              disabled={isScanning}
            >
              {isScanning ? (
                <ActivityIndicator size="large" color="#ffffff" />
              ) : (
                <LinearGradient
                  colors={['#4CAF50', '#45a049']}
                  style={styles.captureButtonInner}
                >
                  <Icon name="camera" size={32} color="#ffffff" />
                </LinearGradient>
              )}
            </TouchableOpacity>
            
            <Text style={styles.captureHint}>
              {isScanning ? 'Analyzing card...' : 'Tap to scan card'}
            </Text>
          </View>
        </View>

        {/* Instructions */}
        <View style={styles.instructionsContainer}>
          <LinearGradient
            colors={['rgba(0,0,0,0.8)', 'transparent']}
            style={styles.instructionsGradient}
          >
            <Text style={styles.instructionsTitle}>
              📱 Instant AI Grading
            </Text>
            <Text style={styles.instructionsText}>
              • Hold phone steady above card{'\n'}
              • Ensure good lighting{'\n'}
              • Keep card flat and centered
            </Text>
          </LinearGradient>
        </View>
      </CameraView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  camera: {
    flex: 1,
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a2e',
    padding: 20,
  },
  permissionText: {
    color: '#ffffff',
    fontSize: 18,
    textAlign: 'center',
    marginVertical: 20,
  },
  permissionButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  permissionButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  topControls: {
    position: 'absolute',
    top: 50,
    right: 20,
    zIndex: 1,
  },
  controlButton: {
    backgroundColor: 'rgba(0,0,0,0.6)',
    padding: 12,
    borderRadius: 25,
    marginBottom: 10,
  },
  overlayContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#000000',
  },
  cardFrame: {
    width: width * 0.8,
    height: (width * 0.8) * 1.4, // Pokemon card aspect ratio
    justifyContent: 'center',
    alignItems: 'center',
  },
  cardFrameContent: {
    width: '100%',
    height: '100%',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#4CAF50',
    borderStyle: 'dashed',
    position: 'relative',
    backgroundColor: 'transparent', // Completely transparent
  },
  cornerGuide: {
    position: 'absolute',
    width: 20,
    height: 20,
    borderColor: '#4CAF50',
    borderWidth: 3,
    top: -2,
    left: -2,
    borderRightWidth: 0,
    borderBottomWidth: 0,
  },
  topRight: {
    top: -2,
    right: -2,
    left: 'auto',
    borderLeftWidth: 0,
    borderBottomWidth: 0,
    borderRightWidth: 3,
  },
  bottomLeft: {
    bottom: -2,
    left: -2,
    top: 'auto',
    borderRightWidth: 0,
    borderTopWidth: 0,
    borderBottomWidth: 3,
  },
  bottomRight: {
    bottom: -2,
    right: -2,
    top: 'auto',
    left: 'auto',
    borderLeftWidth: 0,
    borderTopWidth: 0,
    borderRightWidth: 3,
    borderBottomWidth: 3,
  },
  frameInstructions: {
    position: 'absolute',
    bottom: -80,
    alignItems: 'center',
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 15,
  },
  frameText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  frameSubtext: {
    color: '#ffffff',
    fontSize: 12,
    textAlign: 'center',
    marginTop: 3,
    opacity: 0.9,
  },
  bottomControls: {
    position: 'absolute',
    bottom: 100,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  captureContainer: {
    alignItems: 'center',
  },
  captureButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255,255,255,0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureButtonDisabled: {
    opacity: 0.6,
  },
  captureButtonInner: {
    width: 70,
    height: 70,
    borderRadius: 35,
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureHint: {
    color: '#ffffff',
    fontSize: 16,
    marginTop: 10,
    textAlign: 'center',
  },
  instructionsContainer: {
    position: 'absolute',
    top: 100,
    left: 20,
    right: 20,
  },
  instructionsGradient: {
    padding: 20,
    borderRadius: 10,
  },
  instructionsTitle: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  instructionsText: {
    color: '#ffffff',
    fontSize: 14,
    opacity: 0.9,
    lineHeight: 20,
  },
});