import React, { useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { useAuth } from '../contexts/AuthContext';

const AdminSettings = () => {
  const { authConfig } = useAuth();
  const rbac = authConfig?.rbac || {};
  const rolePermissions = rbac.role_permissions || {};
  const roleLabels = rbac.role_labels || {};
  const roles = useMemo(() => Object.keys(rolePermissions), [rolePermissions]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">System Settings</h1>
      <Card>
        <CardHeader>
          <CardTitle>API Configuration</CardTitle>
          <CardDescription>Manage platform-level configuration</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm text-gray-600 dark:text-gray-400">API Base URL</label>
            <Input
              placeholder="https://api.agrisight.org"
              defaultValue={import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL}
            />
          </div>
          <Button>Save Changes</Button>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>RBAC Map</CardTitle>
          <CardDescription>Role-based access at a glance (from backend)</CardDescription>
        </CardHeader>
        <CardContent>
          {roles.length === 0 ? (
            <div className="text-sm text-gray-600 dark:text-gray-400">
              RBAC configuration not available.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {roles.map((role) => {
                const permissions = rolePermissions[role] || [];
                const label = roleLabels[role] || role;
                return (
                  <div key={role} className="rounded-lg border border-gray-200 dark:border-gray-800 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">
                        {label}
                      </div>
                      <Badge variant="secondary">{role}</Badge>
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400 mb-3">
                      Permissions
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {permissions[0] === '*' ? (
                        <Badge>All Access</Badge>
                      ) : (
                        permissions.map((perm) => (
                          <Badge key={perm} variant="outline">
                            {perm}
                          </Badge>
                        ))
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default AdminSettings;


