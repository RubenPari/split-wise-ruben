import React, { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet, Alert, ScrollView, TouchableOpacity } from 'react-native';
import { api } from '../../services/api';
import { GroupMember, SplitType } from '../../types';

export default function AddExpenseScreen({ navigation, route }: any) {
  const { groupId, members } = route.params;
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [selectedPayer, setSelectedPayer] = useState<number>(members[0]?.user_id || 0);
  const [selectedMembers, setSelectedMembers] = useState<number[]>(members.map((m: GroupMember) => m.user_id));
  const [splitType, setSplitType] = useState<SplitType>('equal');

  const handleCreate = async () => {
    if (!title.trim() || !amount || selectedMembers.length === 0) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }
    const parsedAmount = parseFloat(amount);
    if (isNaN(parsedAmount) || parsedAmount <= 0) {
      Alert.alert('Error', 'Invalid amount');
      return;
    }

    const shareAmount = parsedAmount / selectedMembers.length;

    try {
      await api.createExpense({
        group_id: groupId,
        title,
        amount: parsedAmount,
        date: new Date().toISOString(),
        payer_id: selectedPayer,
        split_type: splitType,
        shares: selectedMembers.map((userId: number) => ({
          user_id: userId,
          share_amount: shareAmount,
        })),
      });
      navigation.goBack();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create expense');
    }
  };

  const toggleMember = (userId: number) => {
    setSelectedMembers(prev => 
      prev.includes(userId) ? prev.filter(id => id !== userId) : [...prev, userId]
    );
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.label}>Title</Text>
      <TextInput style={styles.input} placeholder="What was it for?" value={title} onChangeText={setTitle} />
      
      <Text style={styles.label}>Amount</Text>
      <TextInput style={styles.input} placeholder="0.00" value={amount} onChangeText={setAmount} keyboardType="decimal-pad" />
      
      <Text style={styles.label}>Paid by</Text>
      <View style={styles.membersList}>
        {members.map((m: GroupMember) => (
          <TouchableOpacity
            key={m.user_id}
            style={[styles.memberChip, selectedPayer === m.user_id && styles.selectedChip]}
            onPress={() => setSelectedPayer(m.user_id)}
          >
            <Text style={selectedPayer === m.user_id ? styles.selectedChipText : undefined}>
              {m.user.full_name || m.user.email}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      
      <Text style={styles.label}>Split between</Text>
      <View style={styles.membersList}>
        {members.map((m: GroupMember) => (
          <TouchableOpacity
            key={m.user_id}
            style={[styles.memberChip, selectedMembers.includes(m.user_id) && styles.selectedChip]}
            onPress={() => toggleMember(m.user_id)}
          >
            <Text style={selectedMembers.includes(m.user_id) ? styles.selectedChipText : undefined}>
              {m.user.full_name || m.user.email}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      
      <Button title="Add Expense" onPress={handleCreate} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  label: { fontSize: 16, fontWeight: '600', marginBottom: 8, marginTop: 16 },
  input: { borderWidth: 1, borderColor: '#ddd', padding: 12, borderRadius: 8, fontSize: 16 },
  membersList: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  memberChip: { paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20, backgroundColor: '#eee' },
  selectedChip: { backgroundColor: '#4CAF50' },
  selectedChipText: { color: '#fff' },
});
