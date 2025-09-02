import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';

const Register = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Request Access</CardTitle>
          <CardDescription>We will review and approve eligible requests</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input placeholder="Full name"/>
          <Input placeholder="Work email" type="email"/>
          <Input placeholder="Organization"/>
          <Button className="w-full">Submit Request</Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default Register;


