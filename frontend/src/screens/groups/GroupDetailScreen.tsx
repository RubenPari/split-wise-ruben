import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, Button, Alert } from 'react-native';
import { api } from '../../services/api';
import { Group, Expense } from '../../types';

export default function GroupDetailScreen({ navigation, route }: any) {
  const { groupId } = route.params;
  const [group, setGroup] = useState<Group | null>(null);
  const [expenses, setExpenses] = useState<Expense[]>([]);

  useEffect(() => {
    loadGroupData();
  }, [groupId]);

  const loadGroupData = async () => {
    const [groupData, expensesData] = await Promise.all([
      api.getGroup(groupId),
      api.getGroupExpenses(groupId),
    ]);
    setGroup(groupData);
    setExpenses(expensesData);
  };

  const renderExpense = ({ item }: { item: Expense }) => (
    <TouchableOpacity style={styles.expenseCard}>
      <View style={styles.expenseInfo}>
        <Text style={styles.expenseTitle}>{item.title}</Text>
        <Text style={styles.expenseDate}>{new Date(item.date).toLocaleDateString()}</Text>
      </View>
      <Text style={styles.expenseAmount}>€{item.amount.toFixed(2)}</Text>
    </TouchableOpacity>
  );

  if (!group) return null;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.groupName}>{group.name}</Text>
        <Text style={styles.description}>{group.description || 'No description'}</Text>
        <View style={styles.actions}>
          <Button title="Balances" onPress={() => navigation.navigate('Balances', { groupId })} />
          <Button title="Add Expense" onPress={() => navigation.navigate('AddExpense', { groupId, members: group.members })} />
        </View>
      </View>
      <Text style={styles.sectionTitle}>Recent Expenses</Text>
      <FlatList
        data={expenses}
        renderItem={renderExpense}
        keyExtractor={(item) => item.id.toString()}
        refreshing={false}
        onRefresh={loadGroupData}
        ListEmptyComponent={<Text style={styles.emptyText}>No expenses yet</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  header: { marginBottom: 20 },
  groupName: { fontSize: 24, fontWeight: 'bold' },
  description: { color: '#666', marginTop: 4 },
  actions: { flexDirection: 'row', gap: 10, marginTop: 12 },
  sectionTitle: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
  expenseCard: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', padding: 16, backgroundColor: '#fff', marginBottom: 8, borderRadius: 8 },
  expenseInfo: { flex: 1 },
  expenseTitle: { fontSize: 16 },
  expenseDate: { color: '#666', marginTop: 4 },
  expenseAmount: { fontSize: 16, fontWeight: '600', color: '#4CAF50' },
  emptyText: { textAlign: 'center', color: '#666', marginTop: 20 },
});
