import { useQuery } from '@tanstack/react-query';
import { alertsAPI, analyticsAPI } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';

const REFRESH_MS = 60 * 1000;

/** Badge text for a count: hidden when 0/unknown, "99+" when large. */
export const formatBadgeCount = (count) => {
  if (typeof count !== 'number' || !Number.isFinite(count) || count <= 0) return null;
  return count > 99 ? '99+' : String(count);
};

/**
 * Live counts for the sidebar badges and the header bell. These used to be
 * hard-coded ("3", "5"), which contradicted the pages they linked to.
 */
export const useNavCounts = () => {
  const { isAuthenticated, hasPermission } = useAuth();
  const canSeeStress = isAuthenticated && hasPermission('view_stress_events');

  const unread = useQuery({
    queryKey: ['nav', 'alerts-unread-count'],
    queryFn: () => alertsAPI.getUnreadCount(),
    enabled: isAuthenticated,
    refetchInterval: REFRESH_MS,
    staleTime: REFRESH_MS / 2,
  });

  const stress = useQuery({
    queryKey: ['nav', 'stress-recent-count'],
    queryFn: () => analyticsAPI.getStressEventSummary({ days: 30 }),
    enabled: canSeeStress,
    refetchInterval: REFRESH_MS,
    staleTime: REFRESH_MS / 2,
  });

  return {
    unreadAlerts: unread.data?.unread_count,
    recentStressEvents: stress.data?.recent_events_count,
  };
};

export const useRecentAlerts = (enabled) => {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: ['nav', 'alerts-recent'],
    queryFn: () => alertsAPI.getRecentAlerts(),
    enabled: isAuthenticated && enabled,
    staleTime: REFRESH_MS / 2,
  });
};
