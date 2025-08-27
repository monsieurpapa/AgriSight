import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Bell, 
  User, 
  Settings, 
  LogOut, 
  Menu, 
  X,
  Satellite,
  ChevronDown
} from 'lucide-react';
import { Button } from '../ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { Badge } from '../ui/badge';
import { useAuth } from '../../contexts/AuthContext';
import { cn } from '../../lib/utils';

const Header = ({ onMenuToggle, isMobileMenuOpen }) => {
  const { user, organization, logout } = useAuth();
  const navigate = useNavigate();
  const [notificationCount] = useState(3); // Mock notification count

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleProfileClick = () => {
    navigate('/profile');
  };

  const handleSettingsClick = () => {
    navigate('/settings');
  };

  return (
    <header className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left side - Logo and mobile menu */}
          <div className="flex items-center">
            {/* Mobile menu button */}
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden mr-2"
              onClick={onMenuToggle}
            >
              {isMobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>

            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <div className="flex items-center justify-center w-8 h-8 bg-green-600 rounded-lg">
                <Satellite className="h-5 w-5 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  AgriSight
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400 -mt-1">
                  Agricultural Monitoring
                </p>
              </div>
            </Link>
          </div>

          {/* Center - Organization info (hidden on mobile) */}
          {organization && (
            <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
              <div className="text-center">
                <div className="font-medium">{organization.name}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {organization.organization_type}
                </div>
              </div>
            </div>
          )}

          {/* Right side - Notifications and user menu */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="relative">
                  <Bell className="h-5 w-5" />
                  {notificationCount > 0 && (
                    <Badge 
                      variant="destructive" 
                      className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center text-xs p-0"
                    >
                      {notificationCount}
                    </Badge>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-80">
                <DropdownMenuLabel>Notifications</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <div className="max-h-64 overflow-y-auto">
                  {/* Mock notifications */}
                  <DropdownMenuItem className="flex flex-col items-start p-3">
                    <div className="font-medium text-sm">Agricultural Stress Detected</div>
                    <div className="text-xs text-gray-500 mt-1">
                      NDVI values below threshold in Goma region
                    </div>
                    <div className="text-xs text-gray-400 mt-1">2 hours ago</div>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="flex flex-col items-start p-3">
                    <div className="font-medium text-sm">Processing Complete</div>
                    <div className="text-xs text-gray-500 mt-1">
                      Satellite imagery analysis finished for 3 regions
                    </div>
                    <div className="text-xs text-gray-400 mt-1">4 hours ago</div>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="flex flex-col items-start p-3">
                    <div className="font-medium text-sm">New Report Available</div>
                    <div className="text-xs text-gray-500 mt-1">
                      Weekly agricultural monitoring report is ready
                    </div>
                    <div className="text-xs text-gray-400 mt-1">1 day ago</div>
                  </DropdownMenuItem>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-center text-sm text-blue-600 hover:text-blue-700">
                  View all notifications
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* User menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                    <User className="h-4 w-4" />
                  </div>
                  <div className="hidden sm:block text-left">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {user?.first_name} {user?.last_name}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {user?.role}
                    </div>
                  </div>
                  <ChevronDown className="h-4 w-4 text-gray-500" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">
                      {user?.first_name} {user?.last_name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {user?.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleProfileClick}>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleSettingsClick}>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-red-600">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

