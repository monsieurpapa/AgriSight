/**
 * Role code ('admin', 'humanitarian', ...) for a user from /api/auth/user/.
 *
 * The API returns `user_type` as the *display label* ("Administrator") and
 * `user_type_code` as the machine code. Code that read `user_type` first
 * looked up labels and role permissions with "Administrator", so admins were
 * shown as "User" and role-based permission fallbacks never matched.
 * `user_type` is only used when no code is present (older payloads).
 */
export const getRoleCode = (user) => {
  if (!user) return null;
  return user.user_type_code || user.user_type || null;
};
