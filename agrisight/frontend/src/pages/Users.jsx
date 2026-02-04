import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { usersAPI, organizationsAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Input } from '../components/ui/input';
import { Users as UsersIcon, Plus, RefreshCcw } from 'lucide-react';

const Users = () => {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersAPI.getUsers()
  });
  const { data: orgData } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => organizationsAPI.getOrganizations()
  });

  const organizations = orgData?.results || [];
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    user_type: 'humanitarian',
    organization: '',
    password: '',
    password_confirm: ''
  });
  const [formError, setFormError] = useState(null);

  const createUser = useMutation({
    mutationFn: (payload) => usersAPI.createUser(payload),
    onSuccess: () => {
      setFormData({
        username: '',
        email: '',
        first_name: '',
        last_name: '',
        user_type: 'humanitarian',
        organization: '',
        password: '',
        password_confirm: ''
      });
      setFormError(null);
      setShowForm(false);
      refetch();
    },
    onError: () => {
      setFormError('Failed to create user. Check required fields and permissions.');
    }
  });

  const handleCreate = () => {
    if (!formData.username || !formData.email || !formData.password || !formData.password_confirm) {
      setFormError('Username, email, and password are required.');
      return;
    }

    createUser.mutate({
      ...formData,
      organization: formData.organization || undefined
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Users</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage platform users and roles</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCcw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`}/>Refresh
          </Button>
          <Button onClick={() => setShowForm((prev) => !prev)}>
            <Plus className="h-4 w-4 mr-2"/>Add User
          </Button>
        </div>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create User</CardTitle>
            <CardDescription>Invite a user with role and organization scope</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {formError && <div className="text-sm text-red-600">{formError}</div>}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                placeholder="Username"
                value={formData.username}
                onChange={(event) => setFormData((prev) => ({ ...prev, username: event.target.value }))}
              />
              <Input
                placeholder="Email"
                value={formData.email}
                onChange={(event) => setFormData((prev) => ({ ...prev, email: event.target.value }))}
              />
              <Input
                placeholder="First name"
                value={formData.first_name}
                onChange={(event) => setFormData((prev) => ({ ...prev, first_name: event.target.value }))}
              />
              <Input
                placeholder="Last name"
                value={formData.last_name}
                onChange={(event) => setFormData((prev) => ({ ...prev, last_name: event.target.value }))}
              />
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Role
                <select
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.user_type}
                  onChange={(event) => setFormData((prev) => ({ ...prev, user_type: event.target.value }))}
                >
                  <option value="admin">Administrator</option>
                  <option value="humanitarian">Humanitarian</option>
                  <option value="cooperative">Cooperative</option>
                  <option value="government">Government</option>
                  <option value="researcher">Researcher</option>
                </select>
              </label>
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Organization
                <select
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.organization}
                  onChange={(event) => setFormData((prev) => ({ ...prev, organization: event.target.value }))}
                >
                  <option value="">None</option>
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>{org.name}</option>
                  ))}
                </select>
              </label>
              <Input
                placeholder="Password"
                type="password"
                value={formData.password}
                onChange={(event) => setFormData((prev) => ({ ...prev, password: event.target.value }))}
              />
              <Input
                placeholder="Confirm password"
                type="password"
                value={formData.password_confirm}
                onChange={(event) => setFormData((prev) => ({ ...prev, password_confirm: event.target.value }))}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={createUser.isLoading}>Create</Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
          <CardDescription>Active user accounts</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">Loading users...</div>
          ) : isError ? (
            <div className="py-12 text-center text-red-600">Failed to load users.</div>
          ) : data?.results?.length ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Organization</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.results.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell className="font-medium flex items-center gap-2">
                        <UsersIcon className="h-4 w-4 text-gray-400"/>
                        {user.first_name || user.last_name ? `${user.first_name} ${user.last_name}` : user.username}
                      </TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>{user.user_type}</TableCell>
                      <TableCell>{user.organization_name || '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">No users found.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Users;
