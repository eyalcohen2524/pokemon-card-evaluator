import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Dimensions,
  Alert,
  TextInput,
  Modal,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useNavigation } from '@react-navigation/native';
import RadarChart from '../../components/RadarChart';
import { useVault } from '../../services/VaultService';

const { width } = Dimensions.get('window');

export default function CardDetailScreen({ route }) {
  const { card } = route.params;
  const navigation = useNavigation();
  const { updateCard, deleteCard } = useVault();
  
  const [isEditing, setIsEditing] = useState(false);
  const [editedCard, setEditedCard] = useState(card);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const handleSaveEdit = async () => {
    try {
      await updateCard(card.id, editedCard);
      setIsEditing(false);
      Alert.alert('Success', 'Card updated successfully!');
    } catch (error) {
      Alert.alert('Error', 'Failed to update card. Please try again.');
    }
  };

  const handleDelete = async () => {
    try {
      await deleteCard(card.id);
      setShowDeleteModal(false);
      navigation.goBack();
      Alert.alert('Deleted', 'Card removed from vault.');
    } catch (error) {
      Alert.alert('Error', 'Failed to delete card. Please try again.');
    }
  };

  const getGradeColor = (grade) => {
    const gradeNum = parseFloat(grade);
    if (gradeNum >= 9) return '#4CAF50';
    if (gradeNum >= 8) return '#8BC34A';
    if (gradeNum >= 7) return '#FFC107';
    if (gradeNum >= 6) return '#FF9800';
    return '#F44336';
  };

  const renderEditModal = () => (
    <Modal
      visible={isEditing}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <SafeAreaView style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Edit Card</Text>
          <View style={styles.modalButtons}>
            <TouchableOpacity
              style={styles.modalButton}
              onPress={() => setIsEditing(false)}
            >
              <Text style={styles.modalButtonText}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.modalButton, styles.saveButton]}
              onPress={handleSaveEdit}
            >
              <Text style={[styles.modalButtonText, { color: '#4CAF50' }]}>Save</Text>
            </TouchableOpacity>
          </View>
        </View>

        <ScrollView style={styles.modalContent}>
          <View style={styles.editField}>
            <Text style={styles.editLabel}>Card Name</Text>
            <TextInput
              style={styles.editInput}
              value={editedCard.name}
              onChangeText={(text) => setEditedCard({ ...editedCard, name: text })}
              placeholder="Enter card name"
              placeholderTextColor="#666"
            />
          </View>

          <View style={styles.editField}>
            <Text style={styles.editLabel}>Set</Text>
            <TextInput
              style={styles.editInput}
              value={editedCard.set}
              onChangeText={(text) => setEditedCard({ ...editedCard, set: text })}
              placeholder="Enter set name"
              placeholderTextColor="#666"
            />
          </View>

          <View style={styles.editField}>
            <Text style={styles.editLabel}>Set Number</Text>
            <TextInput
              style={styles.editInput}
              value={editedCard.setNumber}
              onChangeText={(text) => setEditedCard({ ...editedCard, setNumber: text })}
              placeholder="e.g., 4/102"
              placeholderTextColor="#666"
            />
          </View>

          <View style={styles.editField}>
            <Text style={styles.editLabel}>Market Value</Text>
            <TextInput
              style={styles.editInput}
              value={editedCard.marketValue}
              onChangeText={(text) => setEditedCard({ ...editedCard, marketValue: text })}
              placeholder="e.g., $150.00"
              placeholderTextColor="#666"
            />
          </View>

          <View style={styles.editField}>
            <Text style={styles.editLabel}>Notes</Text>
            <TextInput
              style={[styles.editInput, styles.editTextArea]}
              value={editedCard.notes || ''}
              onChangeText={(text) => setEditedCard({ ...editedCard, notes: text })}
              placeholder="Add personal notes about this card..."
              placeholderTextColor="#666"
              multiline
              numberOfLines={4}
            />
          </View>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );

  const renderDeleteModal = () => (
    <Modal
      visible={showDeleteModal}
      transparent={true}
      animationType="fade"
    >
      <View style={styles.deleteModalOverlay}>
        <View style={styles.deleteModalContent}>
          <Icon name="warning" size={50} color="#F44336" />
          <Text style={styles.deleteModalTitle}>Delete Card?</Text>
          <Text style={styles.deleteModalText}>
            Are you sure you want to remove "{card.name}" from your vault? This action cannot be undone.
          </Text>
          <View style={styles.deleteModalButtons}>
            <TouchableOpacity
              style={styles.deleteModalButton}
              onPress={() => setShowDeleteModal(false)}
            >
              <Text style={styles.deleteModalButtonText}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.deleteModalButton, styles.deleteButton]}
              onPress={handleDelete}
            >
              <Text style={[styles.deleteModalButtonText, { color: '#F44336' }]}>
                Delete
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header Actions */}
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => setIsEditing(true)}
          >
            <Icon name="edit" size={20} color="#4CAF50" />
            <Text style={styles.actionButtonText}>Edit</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.actionButton, styles.deleteActionButton]}
            onPress={() => setShowDeleteModal(true)}
          >
            <Icon name="delete" size={20} color="#F44336" />
            <Text style={[styles.actionButtonText, { color: '#F44336' }]}>Delete</Text>
          </TouchableOpacity>
        </View>

        {/* Card Image */}
        {card.photoUri && (
          <View style={styles.imageContainer}>
            <Image 
              source={{ uri: card.photoUri }} 
              style={styles.cardImage}
              resizeMode="contain"
            />
          </View>
        )}

        {/* Card Info */}
        <View style={styles.infoContainer}>
          <LinearGradient
            colors={['#1e3c72', '#2a5298']}
            style={styles.infoGradient}
          >
            <Text style={styles.cardName}>{card.name}</Text>
            <Text style={styles.cardSet}>{card.set}</Text>
            <Text style={styles.cardNumber}>#{card.setNumber}</Text>
            
            <View style={styles.cardMeta}>
              <View style={styles.metaItem}>
                <Icon name="calendar-today" size={16} color="#ffffff" />
                <Text style={styles.metaText}>
                  Scanned {new Date(card.scannedAt).toLocaleDateString()}
                </Text>
              </View>
              <View style={styles.metaItem}>
                <Icon name="camera" size={16} color="#ffffff" />
                <Text style={styles.metaText}>
                  {Math.round(card.confidence * 100)}% confidence
                </Text>
              </View>
            </View>
          </LinearGradient>
        </View>

        {/* Overall Grade */}
        <View style={styles.gradeContainer}>
          <LinearGradient
            colors={[getGradeColor(card.overallGrade), '#333']}
            style={styles.gradeGradient}
          >
            <Text style={styles.gradeLabel}>Overall Grade</Text>
            <Text style={styles.gradeValue}>{card.overallGrade}</Text>
            <View style={styles.gradeStars}>
              {[...Array(5)].map((_, i) => (
                <Icon
                  key={i}
                  name="star"
                  size={24}
                  color={i < Math.floor(parseFloat(card.overallGrade)) ? '#FFD700' : '#666'}
                />
              ))}
            </View>
          </LinearGradient>
        </View>

        {/* Radar Chart */}
        {card.subgrades && Object.keys(card.subgrades).length > 0 && (
          <View style={styles.chartContainer}>
            <Text style={styles.sectionTitle}>Condition Breakdown</Text>
            <RadarChart
              data={card.subgrades}
              size={width - 40}
              maxValue={10}
            />
          </View>
        )}

        {/* Sub-grades Detail */}
        {card.subgrades && (
          <View style={styles.subgradesContainer}>
            <Text style={styles.sectionTitle}>Sub-grades Detail</Text>
            {Object.entries(card.subgrades).map(([key, value]) => (
              <View key={key} style={styles.subgradeRow}>
                <View style={styles.subgradeInfo}>
                  <Text style={styles.subgradeLabel}>
                    {key.charAt(0).toUpperCase() + key.slice(1)}
                  </Text>
                  <Text style={styles.subgradeDescription}>
                    {getSubgradeDescription(key, value)}
                  </Text>
                </View>
                <View style={styles.subgradeValueContainer}>
                  <Text style={[styles.subgradeValue, { color: getGradeColor(value) }]}>
                    {value}
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
                </View>
              </View>
            ))}
          </View>
        )}

        {/* Market Value */}
        <View style={styles.valueContainer}>
          <Text style={styles.sectionTitle}>Market Value</Text>
          <LinearGradient
            colors={['#4CAF50', '#45a049']}
            style={styles.valueGradient}
          >
            <Icon name="attach-money" size={32} color="#ffffff" />
            <Text style={styles.valueAmount}>{card.marketValue}</Text>
            <Text style={styles.valueNote}>Estimated current value</Text>
          </LinearGradient>
        </View>

        {/* Notes */}
        {card.notes && (
          <View style={styles.notesContainer}>
            <Text style={styles.sectionTitle}>Notes</Text>
            <View style={styles.notesCard}>
              <Text style={styles.notesText}>{card.notes}</Text>
            </View>
          </View>
        )}

        {/* Scan Details */}
        <View style={styles.scanDetailsContainer}>
          <Text style={styles.sectionTitle}>Scan Details</Text>
          <View style={styles.scanDetailsCard}>
            <View style={styles.scanDetailRow}>
              <Text style={styles.scanDetailLabel}>Scan Date:</Text>
              <Text style={styles.scanDetailValue}>
                {new Date(card.scannedAt).toLocaleString()}
              </Text>
            </View>
            <View style={styles.scanDetailRow}>
              <Text style={styles.scanDetailLabel}>AI Confidence:</Text>
              <Text style={styles.scanDetailValue}>
                {Math.round(card.confidence * 100)}%
              </Text>
            </View>
            {card.updatedAt && (
              <View style={styles.scanDetailRow}>
                <Text style={styles.scanDetailLabel}>Last Updated:</Text>
                <Text style={styles.scanDetailValue}>
                  {new Date(card.updatedAt).toLocaleString()}
                </Text>
              </View>
            )}
          </View>
        </View>
      </ScrollView>

      {renderEditModal()}
      {renderDeleteModal()}
    </SafeAreaView>
  );
}

function getSubgradeDescription(subgrade, value) {
  const descriptions = {
    centering: value >= 9 ? 'Perfectly centered' : value >= 7 ? 'Well centered' : 'Off-center',
    surface: value >= 9 ? 'Flawless surface' : value >= 7 ? 'Minor surface wear' : 'Visible surface wear',
    edges: value >= 9 ? 'Sharp edges' : value >= 7 ? 'Minor edge wear' : 'Visible edge wear',
    corners: value >= 9 ? 'Sharp corners' : value >= 7 ? 'Minor corner wear' : 'Rounded corners'
  };
  
  return descriptions[subgrade.toLowerCase()] || 'Assessment complete';
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
  headerActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginBottom: 20,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1a1a2e',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginLeft: 10,
  },
  deleteActionButton: {
    backgroundColor: 'rgba(244, 67, 54, 0.1)',
  },
  actionButtonText: {
    color: '#4CAF50',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 5,
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  cardImage: {
    width: width * 0.7,
    height: (width * 0.7) * 1.4,
    borderRadius: 15,
    backgroundColor: '#333',
  },
  infoContainer: {
    marginBottom: 20,
    borderRadius: 15,
    overflow: 'hidden',
  },
  infoGradient: {
    padding: 20,
  },
  cardName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 5,
  },
  cardSet: {
    fontSize: 18,
    color: '#ffffff',
    opacity: 0.8,
    marginBottom: 3,
  },
  cardNumber: {
    fontSize: 16,
    color: '#ffffff',
    opacity: 0.7,
    marginBottom: 15,
  },
  cardMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metaText: {
    color: '#ffffff',
    fontSize: 12,
    opacity: 0.8,
    marginLeft: 5,
  },
  gradeContainer: {
    marginBottom: 25,
    borderRadius: 15,
    overflow: 'hidden',
  },
  gradeGradient: {
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
  },
  gradeStars: {
    flexDirection: 'row',
  },
  chartContainer: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 20,
    marginBottom: 25,
    alignItems: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 15,
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
    marginBottom: 20,
  },
  subgradeInfo: {
    flex: 1,
    marginRight: 15,
  },
  subgradeLabel: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 2,
  },
  subgradeDescription: {
    fontSize: 12,
    color: '#ffffff',
    opacity: 0.7,
  },
  subgradeValueContainer: {
    alignItems: 'flex-end',
    width: 60,
  },
  subgradeValue: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  subgradeBar: {
    width: 50,
    height: 6,
    backgroundColor: '#333',
    borderRadius: 3,
  },
  subgradeProgress: {
    height: 6,
    borderRadius: 3,
  },
  valueContainer: {
    marginBottom: 25,
    borderRadius: 15,
    overflow: 'hidden',
  },
  valueGradient: {
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
  notesContainer: {
    marginBottom: 25,
  },
  notesCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 20,
  },
  notesText: {
    color: '#ffffff',
    fontSize: 16,
    lineHeight: 24,
  },
  scanDetailsContainer: {
    marginBottom: 20,
  },
  scanDetailsCard: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 20,
  },
  scanDetailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  scanDetailLabel: {
    color: '#ffffff',
    fontSize: 14,
    opacity: 0.7,
  },
  scanDetailValue: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  // Modal styles
  modalContainer: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  modalButtons: {
    flexDirection: 'row',
  },
  modalButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginLeft: 10,
  },
  saveButton: {
    backgroundColor: 'rgba(76, 175, 80, 0.1)',
  },
  modalButtonText: {
    color: '#666',
    fontSize: 16,
    fontWeight: 'bold',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  editField: {
    marginBottom: 20,
  },
  editLabel: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  editInput: {
    backgroundColor: '#1a1a2e',
    borderRadius: 10,
    padding: 15,
    color: '#ffffff',
    fontSize: 16,
  },
  editTextArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  // Delete modal styles
  deleteModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  deleteModalContent: {
    backgroundColor: '#1a1a2e',
    borderRadius: 15,
    padding: 30,
    margin: 20,
    alignItems: 'center',
  },
  deleteModalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginVertical: 15,
  },
  deleteModalText: {
    color: '#ffffff',
    fontSize: 16,
    textAlign: 'center',
    opacity: 0.8,
    marginBottom: 25,
    lineHeight: 22,
  },
  deleteModalButtons: {
    flexDirection: 'row',
  },
  deleteModalButton: {
    paddingHorizontal: 25,
    paddingVertical: 12,
    borderRadius: 25,
    marginHorizontal: 10,
    backgroundColor: '#333',
  },
  deleteButton: {
    backgroundColor: 'rgba(244, 67, 54, 0.1)',
  },
  deleteModalButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});