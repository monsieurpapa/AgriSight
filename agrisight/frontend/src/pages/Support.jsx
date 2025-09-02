import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';

const Support = () => (
  <div className="space-y-6">
    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Support</h1>
    <Card>
      <CardHeader>
        <CardTitle>Contact Us</CardTitle>
        <CardDescription>Get help with AgriSight</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-gray-600 dark:text-gray-400">Email: support@agrisight.org</p>
        <Button>Send Message</Button>
      </CardContent>
    </Card>
  </div>
);

export default Support;


