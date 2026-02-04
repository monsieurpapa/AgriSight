import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiKeysAPI, organizationsAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { RefreshCcw, KeyRound, Trash2, RotateCcw, Plus } from 'lucide-react';

const ApiKeys = () => {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['api-keys'],
    queryFn: () => apiKeysAPI.getAPIKeys()
  });
  const { data: orgData } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => organizationsAPI.getOrganizations()
  });
  const organizations = orgData?.results || [];

  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    key_name: '',
    organization: '',
    expires_at: '',
    permissions: ['read']
  });
  const [newKey, setNewKey] = useState(null);

  const createKey = useMutation({
    mutationFn: (payload) => apiKeysAPI.createAPIKey(payload),
    onSuccess: (result) => {
      setNewKey(result.full_api_key || null);
      setShowForm(false);
      setFormData({ key_name: '', organization: '', expires_at: '', permissions: ['read'] });
      refetch();
    }
  });

  const regenerateKey = useMutation({
    mutationFn: (id) => apiKeysAPI.regenerateAPIKey(id),
    onSuccess: (result) => {
      setNewKey(result.new_api_key || null);
      refetch();
    }
  });

  const deleteKey = useMutation({
    mutationFn: (id) => apiKeysAPI.deleteAPIKey(id),
    onSuccess: () => {
      refetch();
    }
  });

  const handleCreate = () => {
    if (!formData.key_name) return;
    createKey.mutate({
      key_name: formData.key_name,
      organization: formData.organization || undefined,
      expires_at: formData.expires_at || null,
      permissions: formData.permissions
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">API Keys</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage API keys and access tokens</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCcw className={`h-4 w-4 mr-2 ${isFetching ? 'animate-spin' : ''}`}/>Refresh
          </Button>
          <Button onClick={() => setShowForm((prev) => !prev)}>
            <Plus className="h-4 w-4 mr-2"/>New Key
          </Button>
        </div>
      </div>

      {newKey && (
        <Card className="border-green-200 bg-green-50 dark:bg-green-900/10">
          <CardHeader>
            <CardTitle>New API Key</CardTitle>
            <CardDescription>This key is only shown once. Store it securely.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between gap-4">
              <code className="text-sm break-all text-green-800 dark:text-green-200">{newKey}</code>
              <Button variant="outline" size="sm" onClick={() => setNewKey(null)}>
                Dismiss
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create API Key</CardTitle>
            <CardDescription>Define key name, expiration, and scope.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Key name"
              value={formData.key_name}
              onChange={(event) => setFormData((prev) => ({ ...prev, key_name: event.target.value }))}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Organization
                <select
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.organization}
                  onChange={(event) => setFormData((prev) => ({ ...prev, organization: event.target.value }))}
                >
                  <option value="">Current Organization</option>
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>{org.name}</option>
                  ))}
                </select>
              </label>
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Expiration Date
                <input
                  type="date"
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.expires_at}
                  onChange={(event) => setFormData((prev) => ({ ...prev, expires_at: event.target.value }))}
                />
              </label>
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={createKey.isLoading}>
                <KeyRound className="h-4 w-4 mr-2"/>Generate
              </Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Active Keys</CardTitle>
          <CardDescription>Keys scoped to your organization(s)</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">Loading keys...</div>
          ) : isError ? (
            <div className="py-12 text-center text-red-600">Failed to load keys.</div>
          ) : data?.results?.length ? (
            data.results.map((key) => (
              <div key={key.id} className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-gray-900 dark:text-white">{key.key_name}</p>
                    <Badge variant={key.is_active ? 'default' : 'secondary'}>
                      {key.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Prefix: {key.key_prefix}</p>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => regenerateKey.mutate(key.id)}>
                    <RotateCcw className="h-4 w-4 mr-1"/>Regenerate
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => deleteKey.mutate(key.id)}>
                    <Trash2 className="h-4 w-4 mr-1"/>Delete
                  </Button>
                </div>
              </div>
            ))
          ) : (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">No API keys available.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ApiKeys;
