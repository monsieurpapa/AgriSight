import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { organizationsAPI } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';
import { Users, Plus, RefreshCcw } from 'lucide-react';
import { Input } from '../components/ui/input';

const Organizations = () => {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => organizationsAPI.getOrganizations(),
  });
  const { data: plansData } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: () => organizationsAPI.getSubscriptionPlans(),
  });

  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    organization_type: 'humanitarian',
    subscription_plan: '',
    contact_email: '',
    contact_phone: '',
    address: ''
  });
  const [formError, setFormError] = useState(null);

  const createOrganization = useMutation({
    mutationFn: (payload) => organizationsAPI.createOrganization(payload),
    onSuccess: () => {
      setFormData({
        name: '',
        organization_type: 'humanitarian',
        subscription_plan: '',
        contact_email: '',
        contact_phone: '',
        address: ''
      });
      setFormError(null);
      setShowForm(false);
      refetch();
    },
    onError: () => {
      setFormError('Failed to create organization.');
    }
  });

  const handleCreate = () => {
    if (!formData.name || !formData.contact_email) {
      setFormError('Name and contact email are required.');
      return;
    }
    createOrganization.mutate({
      ...formData,
      subscription_plan: formData.subscription_plan || undefined,
      contact_phone: formData.contact_phone || undefined,
      address: formData.address || undefined
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Organizations</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage tenant organizations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCcw className="h-4 w-4 mr-2"/>Refresh
          </Button>
          <Button onClick={() => setShowForm((prev) => !prev)}>
            <Plus className="h-4 w-4 mr-2"/>Add Organization
          </Button>
        </div>
      </div>

      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Create Organization</CardTitle>
            <CardDescription>Register a new tenant organization</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {formError && <div className="text-sm text-red-600">{formError}</div>}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                placeholder="Organization name"
                value={formData.name}
                onChange={(event) => setFormData((prev) => ({ ...prev, name: event.target.value }))}
              />
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Type
                <select
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.organization_type}
                  onChange={(event) => setFormData((prev) => ({ ...prev, organization_type: event.target.value }))}
                >
                  <option value="humanitarian">Humanitarian</option>
                  <option value="cooperative">Cooperative</option>
                  <option value="government">Government</option>
                  <option value="researcher">Researcher</option>
                </select>
              </label>
              <label className="text-sm text-gray-700 dark:text-gray-300">
                Subscription Plan
                <select
                  className="mt-1 w-full rounded-md border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm"
                  value={formData.subscription_plan}
                  onChange={(event) => setFormData((prev) => ({ ...prev, subscription_plan: event.target.value }))}
                >
                  <option value="">None</option>
                  {plansData?.results?.map((plan) => (
                    <option key={plan.id} value={plan.id}>{plan.name}</option>
                  ))}
                </select>
              </label>
              <Input
                placeholder="Contact email"
                value={formData.contact_email}
                onChange={(event) => setFormData((prev) => ({ ...prev, contact_email: event.target.value }))}
              />
              <Input
                placeholder="Contact phone"
                value={formData.contact_phone}
                onChange={(event) => setFormData((prev) => ({ ...prev, contact_phone: event.target.value }))}
              />
              <Input
                placeholder="Address"
                value={formData.address}
                onChange={(event) => setFormData((prev) => ({ ...prev, address: event.target.value }))}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={createOrganization.isLoading}>Create</Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>All Organizations</CardTitle>
          <CardDescription>Multi-tenant setup</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">Loading...</div>
          ) : isError ? (
            <div className="py-12 text-center text-red-600">Failed to load.</div>
          ) : data?.results?.length ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Users</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.results.map((org) => (
                    <TableRow key={org.id}>
                      <TableCell className="font-medium flex items-center gap-2">
                        <Users className="h-4 w-4 text-gray-400"/>
                        {org.name}
                      </TableCell>
                      <TableCell>{org.organization_type || '-'}</TableCell>
                      <TableCell>{org.user_count ?? '-'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="py-12 text-center text-gray-600 dark:text-gray-400">No organizations.</div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Organizations;
