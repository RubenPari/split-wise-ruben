import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, Button, Alert } from 'react-native';
import { api } from '../../services/api';
import { GroupBalance, Balance, SimplifiedPayment } from '../../types';

export default function BalancesScreen({ route }: any) {
  const { groupId } = route.params;
  const [balance, setBalance] = useState<GroupBalance | null>(null);

  useEffect(() => {
    loadBalances();
  }, [groupId]);

  const loadBalances = async () => {
    const data = await api.getGroupBalances(groupId);
    setBalance(data);
  };

  const handleSettleUp = async (payment: SimplifiedPayment) => {
    try {
      await api.createPayment(groupId, payment.to_user_id, payment.amount);
      Alert.alert('Success', 'Payment recorded!');
      loadBalances();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to record payment');
    }
  };

  if (!balance) return null;

  const renderBalance = ({ item }: { item: Balance }) => (
    <View style={styles.balanceCard}>
      <Text style={styles.userName}>{item.user.full_name || item.user.email}</Text>
      <Text style={[styles.amount, item.amount >= 0 ? styles.positive : styles.negative]}>
        {item.amount >= 0 ? '+' : ''}€{item.amount.toFixed(2)}
      </Text>
    </View>
  );

  const renderPayment = ({ item }: { item: SimplifiedPayment }) => (
    <View style={styles.paymentCard}>
      <View>
        <Text style={styles.paymentText}>
          {item.from_user.full_name || item.from_user.email} → {item.to_user.full_name || item.to_user.email}
        </Text>
        <Text style={styles.paymentAmount}>€{item.amount.toFixed(2)}</Text>
      </View>
      <Button title="Settle" onPress={() => handleSettleUp(item)} />
    </View>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.sectionTitle}>Current Balances</Text>
      <FlatList data={balance.balances} renderItem={renderBalance} keyExtractor={(item) => item.user_id.toString()} />
      
      <Text style={styles.sectionTitle}>Simplified Payments</Text>
      {balance.simplified_payments.length === 0 ? (
        <Text style={styles.emptyText}>All settled up!</Text>
      ) : (
        <FlatList data={balance.simplified_payments} renderItem={renderPayment} keyExtractor={(item) => `${item.from_user_id}-${item.to_user_id}`} />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  sectionTitle: { fontSize: 18, fontWeight: '600', marginTop: 20, marginBottom: 12 },
  balanceCard: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#fff', marginBottom: 8, borderRadius: 8 },
  userName: { fontSize: 16 },
  amount: { fontSize: 16, fontWeight: '600' },
  positive: { color: '#4CAF50' },
  negative: { color: '#f44336' },
  paymentCard: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#fff', marginBottom: 8, borderRadius: 8 },
  paymentText: { fontSize: 14 },
  paymentAmount: { fontSize: 16, fontWeight: '600', marginTop: 4 },
  emptyText: { textAlign: 'center', color: '#666', marginTop: 20 },
});
