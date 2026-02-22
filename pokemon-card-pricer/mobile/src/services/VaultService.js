import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const VAULT_STORAGE_KEY = '@pokemon_vault_cards';

// Create context
const VaultContext = createContext();

// Provider component
export function VaultProvider({ children }) {
  const [cards, setCards] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadCards();
  }, []);

  /**
   * Load cards from local storage
   */
  const loadCards = async () => {
    try {
      setIsLoading(true);
      const storedCards = await AsyncStorage.getItem(VAULT_STORAGE_KEY);
      
      if (storedCards) {
        const parsedCards = JSON.parse(storedCards);
        setCards(parsedCards);
        console.log(`📱 Loaded ${parsedCards.length} cards from vault`);
      } else {
        console.log('📱 No saved cards found');
        setCards([]);
      }
    } catch (error) {
      console.error('Error loading cards from vault:', error);
      setCards([]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Save cards to local storage
   */
  const saveCards = async (newCards) => {
    try {
      await AsyncStorage.setItem(VAULT_STORAGE_KEY, JSON.stringify(newCards));
      console.log(`💾 Saved ${newCards.length} cards to vault`);
    } catch (error) {
      console.error('Error saving cards to vault:', error);
      throw error;
    }
  };

  /**
   * Add a new card to the vault
   */
  const addCard = async (cardData) => {
    try {
      // Ensure card has required fields
      const card = {
        id: cardData.id || Date.now().toString(),
        name: cardData.name,
        set: cardData.set || 'Unknown Set',
        setNumber: cardData.setNumber || 'Unknown',
        overallGrade: cardData.overallGrade || 'N/A',
        subgrades: cardData.subgrades || {},
        marketValue: cardData.marketValue || 'N/A',
        photoUri: cardData.photoUri,
        scannedAt: cardData.scannedAt || new Date().toISOString(),
        confidence: cardData.confidence || 0,
        notes: cardData.notes || '',
        tags: cardData.tags || [],
        ...cardData // Allow additional fields
      };

      const newCards = [card, ...cards];
      setCards(newCards);
      await saveCards(newCards);
      
      console.log(`✅ Added ${card.name} to vault`);
      return card;
    } catch (error) {
      console.error('Error adding card to vault:', error);
      throw error;
    }
  };

  /**
   * Update an existing card in the vault
   */
  const updateCard = async (cardId, updates) => {
    try {
      const updatedCards = cards.map(card => 
        card.id === cardId 
          ? { ...card, ...updates, updatedAt: new Date().toISOString() }
          : card
      );
      
      setCards(updatedCards);
      await saveCards(updatedCards);
      
      console.log(`📝 Updated card ${cardId}`);
      return updatedCards.find(card => card.id === cardId);
    } catch (error) {
      console.error('Error updating card:', error);
      throw error;
    }
  };

  /**
   * Delete a card from the vault
   */
  const deleteCard = async (cardId) => {
    try {
      const updatedCards = cards.filter(card => card.id !== cardId);
      setCards(updatedCards);
      await saveCards(updatedCards);
      
      console.log(`🗑️ Deleted card ${cardId}`);
    } catch (error) {
      console.error('Error deleting card:', error);
      throw error;
    }
  };

  /**
   * Get a card by ID
   */
  const getCardById = (cardId) => {
    return cards.find(card => card.id === cardId);
  };

  /**
   * Search cards in vault
   */
  const searchCards = (query) => {
    const lowercaseQuery = query.toLowerCase();
    return cards.filter(card => 
      card.name.toLowerCase().includes(lowercaseQuery) ||
      card.set.toLowerCase().includes(lowercaseQuery) ||
      card.setNumber.toLowerCase().includes(lowercaseQuery)
    );
  };

  /**
   * Get cards filtered by criteria
   */
  const getFilteredCards = (filters) => {
    let filteredCards = [...cards];

    if (filters.minGrade) {
      filteredCards = filteredCards.filter(card => 
        parseFloat(card.overallGrade) >= filters.minGrade
      );
    }

    if (filters.maxGrade) {
      filteredCards = filteredCards.filter(card => 
        parseFloat(card.overallGrade) <= filters.maxGrade
      );
    }

    if (filters.set) {
      filteredCards = filteredCards.filter(card => 
        card.set.toLowerCase().includes(filters.set.toLowerCase())
      );
    }

    if (filters.tags && filters.tags.length > 0) {
      filteredCards = filteredCards.filter(card => 
        card.tags && card.tags.some(tag => filters.tags.includes(tag))
      );
    }

    return filteredCards;
  };

  /**
   * Get total collection value
   */
  const getTotalValue = () => {
    return cards.reduce((total, card) => {
      if (card.marketValue && card.marketValue !== 'N/A') {
        const value = parseFloat(card.marketValue.replace('$', '').replace(',', '')) || 0;
        return total + value;
      }
      return total;
    }, 0);
  };

  /**
   * Get collection statistics
   */
  const getCollectionStats = () => {
    if (cards.length === 0) {
      return {
        totalCards: 0,
        totalValue: 0,
        averageGrade: 0,
        gradeCounts: {},
        setCounts: {},
        topCards: []
      };
    }

    // Grade distribution
    const gradeCounts = {};
    const validGrades = cards.filter(card => 
      card.overallGrade !== 'N/A' && !isNaN(parseFloat(card.overallGrade))
    );

    validGrades.forEach(card => {
      const grade = Math.floor(parseFloat(card.overallGrade));
      gradeCounts[grade] = (gradeCounts[grade] || 0) + 1;
    });

    // Set distribution
    const setCounts = {};
    cards.forEach(card => {
      setCounts[card.set] = (setCounts[card.set] || 0) + 1;
    });

    // Average grade
    const totalGrade = validGrades.reduce((sum, card) => 
      sum + parseFloat(card.overallGrade), 0
    );
    const averageGrade = validGrades.length > 0 ? totalGrade / validGrades.length : 0;

    // Top valuable cards
    const topCards = cards
      .filter(card => card.marketValue !== 'N/A')
      .sort((a, b) => {
        const aValue = parseFloat(a.marketValue.replace('$', '').replace(',', '')) || 0;
        const bValue = parseFloat(b.marketValue.replace('$', '').replace(',', '')) || 0;
        return bValue - aValue;
      })
      .slice(0, 5);

    return {
      totalCards: cards.length,
      totalValue: getTotalValue(),
      averageGrade: Math.round(averageGrade * 10) / 10,
      gradeCounts,
      setCounts,
      topCards
    };
  };

  /**
   * Export vault data
   */
  const exportVault = () => {
    try {
      const exportData = {
        exportedAt: new Date().toISOString(),
        version: '1.0',
        totalCards: cards.length,
        cards: cards.map(card => ({
          ...card,
          // Remove photo URI for privacy/size
          photoUri: null
        }))
      };
      
      return JSON.stringify(exportData, null, 2);
    } catch (error) {
      console.error('Error exporting vault:', error);
      throw error;
    }
  };

  /**
   * Import vault data
   */
  const importVault = async (jsonData, options = {}) => {
    try {
      const importData = JSON.parse(jsonData);
      
      if (!importData.cards || !Array.isArray(importData.cards)) {
        throw new Error('Invalid import data format');
      }

      let newCards;
      
      if (options.merge) {
        // Merge with existing cards (avoid duplicates by ID)
        const existingIds = new Set(cards.map(card => card.id));
        const uniqueImportCards = importData.cards.filter(
          card => !existingIds.has(card.id)
        );
        newCards = [...cards, ...uniqueImportCards];
      } else {
        // Replace all cards
        newCards = importData.cards;
      }

      setCards(newCards);
      await saveCards(newCards);
      
      console.log(`📥 Imported ${importData.cards.length} cards`);
      return {
        imported: importData.cards.length,
        total: newCards.length
      };
    } catch (error) {
      console.error('Error importing vault:', error);
      throw error;
    }
  };

  /**
   * Clear all cards from vault
   */
  const clearVault = async () => {
    try {
      setCards([]);
      await AsyncStorage.removeItem(VAULT_STORAGE_KEY);
      console.log('🧹 Cleared vault');
    } catch (error) {
      console.error('Error clearing vault:', error);
      throw error;
    }
  };

  /**
   * Refresh cards (reload from storage)
   */
  const refreshCards = async () => {
    await loadCards();
  };

  const value = {
    // State
    cards,
    isLoading,
    
    // Actions
    addCard,
    updateCard,
    deleteCard,
    getCardById,
    searchCards,
    getFilteredCards,
    
    // Computed values
    getTotalValue,
    getCollectionStats,
    
    // Utility
    exportVault,
    importVault,
    clearVault,
    refreshCards,
  };

  return (
    <VaultContext.Provider value={value}>
      {children}
    </VaultContext.Provider>
  );
}

// Hook to use vault context
export function useVault() {
  const context = useContext(VaultContext);
  if (!context) {
    throw new Error('useVault must be used within a VaultProvider');
  }
  return context;
}