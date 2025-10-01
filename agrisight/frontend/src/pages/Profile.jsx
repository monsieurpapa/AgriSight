import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { User, Mail, Phone, Building, Calendar, Shield, Edit3, Save, X } from 'lucide-react';

const Profile = () => {
  const { user, updateUser, changePassword } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [formData, setFormData] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone_number: user?.phone_number || '',
  });
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password1: '',
    new_password2: '',
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSave = async () => {
    try {
      setError('');
      const result = await updateUser(formData);
      if (result.success) {
        setMessage('Profile updated successfully!');
        setIsEditing(false);
        setTimeout(() => setMessage(''), 3000);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to update profile');
    }
  };

  const handlePasswordSave = async () => {
    try {
      setError('');
      if (passwordData.new_password1 !== passwordData.new_password2) {
        setError('New passwords do not match');
        return;
      }
      const result = await changePassword(passwordData);
      if (result.success) {
        setMessage('Password changed successfully!');
        setIsChangingPassword(false);
        setPasswordData({ old_password: '', new_password1: '', new_password2: '' });
        setTimeout(() => setMessage(''), 3000);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError('Failed to change password');
    }
  };

  const handleCancel = () => {
    setFormData({
      first_name: user?.first_name || '',
      last_name: user?.last_name || '',
      phone_number: user?.phone_number || '',
    });
    setIsEditing(false);
    setError('');
  };

  const handlePasswordCancel = () => {
    setPasswordData({ old_password: '', new_password1: '', new_password2: '' });
    setIsChangingPassword(false);
    setError('');
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Profile</h1>
        {!isEditing && (
          <Button onClick={() => setIsEditing(true)} variant="outline" size="sm">
            <Edit3 className="w-4 h-4 mr-2" />
            Edit Profile
          </Button>
        )}
      </div>

      {message && (
        <Alert>
          <AlertDescription>{message}</AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="w-5 h-5 mr-2" />
              Personal Information
            </CardTitle>
            <CardDescription>Your personal details and contact information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isEditing ? (
              <>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="first_name">First Name</Label>
                    <Input
                      id="first_name"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleInputChange}
                    />
                  </div>
                  <div>
                    <Label htmlFor="last_name">Last Name</Label>
                    <Input
                      id="last_name"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="phone_number">Phone Number</Label>
                  <Input
                    id="phone_number"
                    name="phone_number"
                    value={formData.phone_number}
                    onChange={handleInputChange}
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
                <div className="flex gap-2">
                  <Button onClick={handleSave} size="sm">
                    <Save className="w-4 h-4 mr-2" />
                    Save Changes
                  </Button>
                  <Button onClick={handleCancel} variant="outline" size="sm">
                    <X className="w-4 h-4 mr-2" />
                    Cancel
                  </Button>
                </div>
              </>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center">
                  <User className="w-4 h-4 mr-2 text-gray-500" />
                  <span className="text-sm text-gray-500">Name:</span>
                  <span className="ml-2 font-medium">{user?.first_name} {user?.last_name}</span>
                </div>
                <div className="flex items-center">
                  <Mail className="w-4 h-4 mr-2 text-gray-500" />
                  <span className="text-sm text-gray-500">Email:</span>
                  <span className="ml-2 font-medium">{user?.email}</span>
                </div>
                <div className="flex items-center">
                  <Phone className="w-4 h-4 mr-2 text-gray-500" />
                  <span className="text-sm text-gray-500">Phone:</span>
                  <span className="ml-2 font-medium">{user?.phone_number || 'Not provided'}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Account Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Shield className="w-5 h-5 mr-2" />
              Account Information
            </CardTitle>
            <CardDescription>Your account status and role information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center">
              <Shield className="w-4 h-4 mr-2 text-gray-500" />
              <span className="text-sm text-gray-500">Role:</span>
              <Badge variant="secondary" className="ml-2">
                {user?.user_type || 'User'}
              </Badge>
            </div>
            {user?.organization && (
              <div className="flex items-center">
                <Building className="w-4 h-4 mr-2 text-gray-500" />
                <span className="text-sm text-gray-500">Organization:</span>
                <span className="ml-2 font-medium">{user.organization.name}</span>
              </div>
            )}
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-2 text-gray-500" />
              <span className="text-sm text-gray-500">Member since:</span>
              <span className="ml-2 font-medium">{formatDate(user?.date_joined)}</span>
            </div>
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-2 text-gray-500" />
              <span className="text-sm text-gray-500">Last login:</span>
              <span className="ml-2 font-medium">{formatDate(user?.last_login)}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Password Change */}
      <Card>
        <CardHeader>
          <CardTitle>Security</CardTitle>
          <CardDescription>Change your password to keep your account secure</CardDescription>
        </CardHeader>
        <CardContent>
          {isChangingPassword ? (
            <div className="space-y-4">
              <div>
                <Label htmlFor="old_password">Current Password</Label>
                <Input
                  id="old_password"
                  name="old_password"
                  type="password"
                  value={passwordData.old_password}
                  onChange={handlePasswordChange}
                />
              </div>
              <div>
                <Label htmlFor="new_password1">New Password</Label>
                <Input
                  id="new_password1"
                  name="new_password1"
                  type="password"
                  value={passwordData.new_password1}
                  onChange={handlePasswordChange}
                />
              </div>
              <div>
                <Label htmlFor="new_password2">Confirm New Password</Label>
                <Input
                  id="new_password2"
                  name="new_password2"
                  type="password"
                  value={passwordData.new_password2}
                  onChange={handlePasswordChange}
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handlePasswordSave} size="sm">
                  <Save className="w-4 h-4 mr-2" />
                  Change Password
                </Button>
                <Button onClick={handlePasswordCancel} variant="outline" size="sm">
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <Button onClick={() => setIsChangingPassword(true)} variant="outline">
              Change Password
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Profile;


