import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';

const ForgotPassword = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Reset Password</CardTitle>
          <CardDescription>Enter your email, we'll send a reset link</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input placeholder="Work email" type="email"/>
          <Button className="w-full">Send Reset Link</Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default ForgotPassword;


