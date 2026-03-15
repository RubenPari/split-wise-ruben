import React, { useEffect } from 'react';
import { StatusBar } from 'react-native';
import RootNavigator from './navigation/RootNavigator';
import { useAuthStore } from './store';

export default function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <>
      <StatusBar barStyle="dark-content" />
      <RootNavigator />
    </>
  );
}
