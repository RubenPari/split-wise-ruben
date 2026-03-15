import React, { useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet, Button } from 'react-native';
import { useGroupStore } from '../../store';
import { Group } from '../../types';

export default function GroupsListScreen({ navigation }: any) {
  const { groups, fetchGroups, isLoading } = useGroupStore();

  useEffect(() => {
    fetchGroups();
  }, []);

  const renderGroup = ({ item }: { item: Group }) => (
    <TouchableOpacity 
      style={styles.groupCard}
      onPress={() => navigation.navigate('GroupDetail', { groupId: item.id })}
    >
      <View style={styles.groupIcon}>
        <Text style={styles.groupIconText}>{item.name.charAt(0)}</Text>
      </View>
      <View style={styles.groupInfo}>
        <Text style={styles.groupName}>{item.name}</Text>
        <Text style={styles.memberCount}>{item.members.length} members</Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={groups}
        renderItem={renderGroup}
        keyExtractor={(item) => item.id.toString()}
        refreshing={isLoading}
        onRefresh={fetchGroups}
        ListEmptyComponent={<Text style={styles.emptyText}>No groups yet</Text>}
      />
      <Button title="Create Group" onPress={() => navigation.navigate('CreateGroup')} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  groupCard: { flexDirection: 'row', alignItems: 'center', padding: 16, backgroundColor: '#fff', marginBottom: 12, borderRadius: 12, elevation: 2 },
  groupIcon: { width: 50, height: 50, borderRadius: 25, backgroundColor: '#4CAF50', justifyContent: 'center', alignItems: 'center' },
  groupIconText: { color: '#fff', fontSize: 20, fontWeight: 'bold' },
  groupInfo: { marginLeft: 16 },
  groupName: { fontSize: 18, fontWeight: '600' },
  memberCount: { color: '#666', marginTop: 4 },
  emptyText: { textAlign: 'center', color: '#666', marginTop: 40 },
});
