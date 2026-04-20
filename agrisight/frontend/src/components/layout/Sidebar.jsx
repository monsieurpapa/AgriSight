import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Map,
  Satellite,
  BarChart3,
  AlertTriangle,
  FileText,
  Settings,
  Users,
  MapPin,
  Activity,
  TrendingUp,
  Bell,
  Download,
  X,
  KeyRound,
  ShieldAlert,
} from 'lucide-react';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { cn } from '../../lib/utils';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { user, hasRole, hasPermission, getUserType, getUserTypeLabel } = useAuth();

  const navigationItems = [
    {
      title: 'Overview',
      items: [
        {
          name: 'Dashboard',
          href: '/',
          icon: LayoutDashboard,
          description: 'Main overview and statistics',
          permission: 'view_data',
        },
        {
          name: 'Map View',
          href: '/map',
          icon: Map,
          description: 'Interactive satellite map',
          permission: 'view_data',
        },
      ],
    },
    {
      title: 'Monitoring',
      items: [
        {
          name: 'Regions',
          href: '/regions',
          icon: MapPin,
          description: 'Manage monitoring regions',
          permission: 'manage_regions',
        },
        {
          name: 'Satellite Data',
          href: '/satellite',
          icon: Satellite,
          description: 'Satellite imagery and processing',
          permission: 'view_data',
        },
        {
          name: 'Vegetation Indices',
          href: '/vegetation',
          icon: Activity,
          description: 'NDVI, EVI, NDWI, SAVI analysis',
          permission: 'view_analytics',
        },
        {
          name: 'Analytics',
          href: '/analytics',
          icon: BarChart3,
          description: 'Advanced data analysis',
          permission: 'view_analytics',
        },
      ],
    },
    {
      title: 'Alerts & Reports',
      items: [
        {
          name: 'Stress Events',
          href: '/stress-events',
          icon: AlertTriangle,
          description: 'Agricultural stress monitoring',
          badge: '3',
          permission: 'view_stress_events',
        },
        {
          name: 'Alerts',
          href: '/alerts',
          icon: Bell,
          description: 'System notifications',
          badge: '5',
          permission: 'view_data',
        },
        {
          name: 'Reports',
          href: '/reports',
          icon: FileText,
          description: 'Generate and view reports',
          permission: 'generate_reports',
        },
        {
          name: 'Conflict Reports',
          href: '/conflict-reports',
          icon: ShieldAlert,
          description: 'IPC-aligned district risk PDF reports for DRC',
          permission: 'generate_reports',
        },
        {
          name: 'Exports',
          href: '/exports',
          icon: Download,
          description: 'Data export and downloads',
          permission: 'export_data',
        },
      ],
    },
  ];

  // Add admin-only items
  if (hasRole('admin') || hasPermission('manage_organizations')) {
    navigationItems.push({
      title: 'Administration',
      items: [
        {
          name: 'Organizations',
          href: '/organizations',
          icon: Users,
          description: 'Manage organizations',
          permission: 'manage_organizations',
        },
        {
          name: 'Users',
          href: '/admin/users',
          icon: Users,
          description: 'Manage users and roles',
          permission: 'admin_access',
        },
        {
          name: 'API Keys',
          href: '/admin/api-keys',
          icon: KeyRound,
          description: 'Manage API keys',
          permission: 'admin_access',
        },
        {
          name: 'System Settings',
          href: '/admin/settings',
          icon: Settings,
          description: 'System configuration',
          permission: 'admin_access',
        },
        {
          name: 'Performance',
          href: '/admin/performance',
          icon: TrendingUp,
          description: 'System performance metrics',
          permission: 'admin_access',
        },
      ],
    });
  }

  // Filter navigation items based on permissions
  const filteredNavigationItems = navigationItems.map(section => ({
    ...section,
    items: section.items.filter(item => {
      if (!item.permission) return true;
      return hasPermission(item.permission);
    })
  })).filter(section => section.items.length > 0);

  const isActiveLink = (href) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 z-50 h-full w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transform transition-transform duration-200 ease-in-out md:translate-x-0 md:static md:z-auto",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Mobile close button */}
        <div className="flex items-center justify-between p-4 md:hidden">
          <div className="flex items-center space-x-2">
            <div className="flex items-center justify-center w-8 h-8 bg-green-600 rounded-lg">
              <Satellite className="h-5 w-5 text-white" />
            </div>
            <span className="text-lg font-semibold text-gray-900 dark:text-white">
              AgriSight
            </span>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-4 space-y-6 overflow-y-auto scrollbar-thin">
          {filteredNavigationItems.length === 0 && (
            <div className="px-3 py-4 text-sm text-gray-600 dark:text-gray-400">
              No modules are available for your account yet.
              <div className="mt-2">
                <Link to="/profile" onClick={onClose} className="text-green-600 hover:underline">
                  View profile
                </Link>
              </div>
            </div>
          )}
          {filteredNavigationItems.map((section) => (
            <div key={section.title}>
              <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">
                {section.title}
              </h3>
              <div className="space-y-1">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = isActiveLink(item.href);
                  
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      onClick={onClose}
                      className={cn(
                        "group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150",
                        isActive
                          ? "bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300"
                          : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white"
                      )}
                    >
                      <Icon
                        className={cn(
                          "mr-3 h-5 w-5 flex-shrink-0",
                          isActive
                            ? "text-green-600 dark:text-green-400"
                            : "text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300"
                        )}
                      />
                      <span className="flex-1">{item.name}</span>
                      {item.badge && (
                        <Badge 
                          variant={isActive ? "default" : "secondary"}
                          className="ml-2 text-xs"
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* User info at bottom */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {user?.first_name?.[0] || user?.email?.[0] || 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {user?.email}
              </p>
              <p className="text-xs text-blue-600 dark:text-blue-400 truncate">
                {getUserTypeLabel()}
              </p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
