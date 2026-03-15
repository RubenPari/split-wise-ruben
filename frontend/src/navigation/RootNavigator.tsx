import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { useAuthStore } from '../store';
import LoginScreen from '../screens/auth/LoginScreen';
import RegisterScreen from '../screens/auth/RegisterScreen';
import GroupsListScreen from '../screens/groups/GroupsListScreen';
import GroupDetailScreen from '../screens/groups/GroupDetailScreen';
import CreateGroupScreen from '../screens/groups/CreateGroupScreen';
import AddExpenseScreen from '../screens/expenses/AddExpenseScreen';
import BalancesScreen from '../screens/balances/BalancesScreen';
import { Icon } from 'react-native-elements';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function GroupsStack() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="GroupsList" component={GroupsListScreen} options={{ title: 'My Groups' }} />
      <Stack.Screen name="GroupDetail" component={GroupDetailScreen} options={{ title: 'Group' }} />
      <Stack.Screen name="CreateGroup" component={CreateGroupScreen} options={{ title: 'New Group' }} />
      <Stack.Screen name="AddExpense" component={AddExpenseScreen} options={{ title: 'Add Expense' }} />
      <Stack.Screen name="Balances" component={BalancesScreen} options={{ title: 'Balances' }} />
    </Stack.Navigator>
  );
}

function MainTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen 
        name="Groups" 
        component={GroupsStack}
        options={{ 
          headerShown: false,
          tabBarIcon: ({ color, size }) => <Icon name="people" type="ionicon" color={color} size={size} /> 
        }} 
      />
      <Tab.Screen 
        name="Activity" 
        component={ActivityScreen}
        options={{ 
          title: 'Activity',
          tabBarIcon: ({ color, size }) => <Icon name="time" type="ionicon" color={color} size={size} /> 
        }} 
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{ 
          title: 'Profile',
          tabBarIcon: ({ color, size }) => <Icon name="person" type="ionicon" color={color} size={size} /> 
        }} 
      />
    </Tab.Navigator>
  );
}

function ActivityScreen() {
  return <></>;
}

function ProfileScreen() {
  return <></>;
}

export default function RootNavigator() {
  const { user, isLoading } = useAuthStore();

  if (isLoading) {
    return null;
  }

  return (
    <NavigationContainer>
      <Stack.Navigator>
        {!user ? (
          <>
            <Stack.Screen name="Login" component={LoginScreen} options={{ headerShown: false }} />
            <Stack.Screen name="Register" component={RegisterScreen} options={{ headerShown: false }} />
          </>
        ) : (
          <Stack.Screen name="Main" component={MainTabs} options={{ headerShown: false }} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
