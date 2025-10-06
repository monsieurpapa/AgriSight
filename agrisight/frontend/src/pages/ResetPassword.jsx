import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Eye, EyeOff, Satellite, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Alert, AlertDescription } from '../components/ui/alert';
import { useAuth } from '../contexts/AuthContext';

const ResetPassword = () => {
  const [formData, setFormData] = useState({
    new_password1: '',
    new_password2: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [searchParams] = useSearchParams();
  
  const { confirmPasswordReset } = useAuth();
  const navigate = useNavigate();

  const uid = searchParams.get('uid');
  const token = searchParams.get('token');

  useEffect(() => {
    if (!uid || !token) {
      setError('Invalid reset link. Please request a new password reset.');
    }
  }, [uid, token]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (error) {
      setError('');
    }
  };

  const validatePassword = (password) => {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return {
      isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers,
      errors: [
        password.length < minLength && `At least ${minLength} characters`,
        !hasUpperCase && 'One uppercase letter',
        !hasLowerCase && 'One lowercase letter',
        !hasNumbers && 'One number',
        !hasSpecialChar && 'One special character'
      ].filter(Boolean)
    };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.new_password1 || !formData.new_password2) {
      setError('Please fill in all fields');
      return;
    }

    if (formData.new_password1 !== formData.new_password2) {
      setError('Passwords do not match');
      return;
    }

    const passwordValidation = validatePassword(formData.new_password1);
    if (!passwordValidation.isValid) {
      setError(`Password requirements not met: ${passwordValidation.errors.join(', ')}`);
      return;
    }

    setIsLoading(true);
    setError('');
    
    try {
      const result = await confirmPasswordReset({
        uid,
        token,
        new_password1: formData.new_password1,
        new_password2: formData.new_password2
      });
      
      if (result.success) {
        setSuccess(true);
        setTimeout(() => {
          navigate('/login', { 
            state: { message: 'Password reset successful. Please log in with your new password.' }
          });
        }, 3000);
      } else {
        setError(result.error || 'Failed to reset password');
      }
    } catch (error) {
      console.error('Password reset error:', error);
      setError('An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Password Reset Successful!</h2>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                  Your password has been successfully reset. You will be redirected to the login page shortly.
                </p>
              </div>
              <Button 
                onClick={() => navigate('/login')} 
                className="w-full"
              >
                Go to Login
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-4">
            <Satellite className="w-6 h-6 text-green-600 dark:text-green-400" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900 dark:text-white">
            Reset Your Password
          </CardTitle>
          <CardDescription>
            Enter your new password below
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="new_password1">New Password</Label>
              <div className="relative">
                <Input
                  id="new_password1"
                  name="new_password1"
                  type={showPassword ? "text" : "password"}
                  value={formData.new_password1}
                  onChange={handleInputChange}
                  placeholder="Enter your new password"
                  required
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {formData.new_password1 && (
                <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                  <div className="space-y-1">
                    <div className={`flex items-center ${formData.new_password1.length >= 8 ? 'text-green-600' : 'text-gray-400'}`}>
                      <div className={`w-1.5 h-1.5 rounded-full mr-2 ${formData.new_password1.length >= 8 ? 'bg-green-600' : 'bg-gray-300'}`} />
                      At least 8 characters
                    </div>
                    <div className={`flex items-center ${/[A-Z]/.test(formData.new_password1) ? 'text-green-600' : 'text-gray-400'}`}>
                      <div className={`w-1.5 h-1.5 rounded-full mr-2 ${/[A-Z]/.test(formData.new_password1) ? 'bg-green-600' : 'bg-gray-300'}`} />
                      One uppercase letter
                    </div>
                    <div className={`flex items-center ${/[a-z]/.test(formData.new_password1) ? 'text-green-600' : 'text-gray-400'}`}>
                      <div className={`w-1.5 h-1.5 rounded-full mr-2 ${/[a-z]/.test(formData.new_password1) ? 'bg-green-600' : 'bg-gray-300'}`} />
                      One lowercase letter
                    </div>
                    <div className={`flex items-center ${/\d/.test(formData.new_password1) ? 'text-green-600' : 'text-gray-400'}`}>
                      <div className={`w-1.5 h-1.5 rounded-full mr-2 ${/\d/.test(formData.new_password1) ? 'bg-green-600' : 'bg-gray-300'}`} />
                      One number
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div>
              <Label htmlFor="new_password2">Confirm New Password</Label>
              <div className="relative">
                <Input
                  id="new_password2"
                  name="new_password2"
                  type={showConfirmPassword ? "text" : "password"}
                  value={formData.new_password2}
                  onChange={handleInputChange}
                  placeholder="Confirm your new password"
                  required
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              {formData.new_password2 && formData.new_password1 !== formData.new_password2 && (
                <p className="mt-1 text-xs text-red-600">Passwords do not match</p>
              )}
            </div>

            <Button 
              type="submit" 
              className="w-full" 
              disabled={isLoading || !uid || !token}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Resetting Password...
                </>
              ) : (
                'Reset Password'
              )}
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Remember your password?{' '}
              <Link 
                to="/login" 
                className="text-green-600 hover:text-green-500 font-medium"
              >
                Sign in
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ResetPassword;
