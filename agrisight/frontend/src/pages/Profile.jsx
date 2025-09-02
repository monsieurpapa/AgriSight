import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';

const Profile = () => {
  const { user } = useAuth();
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Profile</h1>
      <Card>
        <CardHeader>
          <CardTitle>User Details</CardTitle>
          <CardDescription>Your account information</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div><span className="text-gray-500">Name:</span> <span className="ml-2">{user?.first_name} {user?.last_name}</span></div>
            <div><span className="text-gray-500">Email:</span> <span className="ml-2">{user?.email}</span></div>
            <div><span className="text-gray-500">Role:</span> <span className="ml-2">{user?.role}</span></div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;


