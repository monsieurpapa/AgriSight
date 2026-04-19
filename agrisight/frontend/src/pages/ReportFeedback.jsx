import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { conflictReportsAPI } from '../lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { CheckCircle, AlertTriangle } from 'lucide-react';

export default function ReportFeedback() {
  const { feedbackToken } = useParams();
  const [rating, setRating] = useState(null);
  const [missingData, setMissingData] = useState('');
  const [wouldUseAgain, setWouldUseAgain] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const submit = useMutation({
    mutationFn: (payload) => conflictReportsAPI.submitFeedback(feedbackToken, payload),
    onSuccess: () => setSubmitted(true),
    onError: (err) => {
      const detail = err?.response?.data?.detail;
      setError(detail || 'Failed to submit feedback. The link may have expired.');
    },
  });

  function handleSubmit(e) {
    e.preventDefault();
    setError('');
    if (!rating) {
      setError('Please select an accuracy rating.');
      return;
    }
    submit.mutate({
      accuracy_rating: rating,
      missing_data: missingData,
      would_use_again: wouldUseAgain,
    });
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardContent className="pt-8 pb-8 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Thank you!</h2>
            <p className="text-gray-500 text-sm">
              Your feedback helps calibrate AgriSight's conflict-awareness model.
              We'll incorporate it before the next report cycle.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <Card className="max-w-lg w-full">
        <CardHeader>
          <CardTitle>Rate this Report</CardTitle>
          <p className="text-sm text-gray-500">
            AgriSight — conflict-aware food security report feedback. Takes 60 seconds.
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Accuracy rating */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                How accurate was the district risk classification? *
              </label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((n) => (
                  <button
                    key={n}
                    type="button"
                    onClick={() => setRating(n)}
                    className={`w-10 h-10 rounded-full border-2 text-sm font-semibold transition-colors ${
                      rating === n
                        ? 'border-green-600 bg-green-600 text-white'
                        : 'border-gray-300 text-gray-600 hover:border-green-400'
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-400 mt-1">1 = very inaccurate &nbsp; 5 = very accurate</p>
            </div>

            {/* Missing data */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                What data was missing or wrong? (optional)
              </label>
              <textarea
                value={missingData}
                onChange={(e) => setMissingData(e.target.value)}
                rows={3}
                placeholder="e.g. ACLED conflict counts looked low for Masisi, displacement figures seem outdated..."
                className="w-full border rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>

            {/* Would use again */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Would you use this report in your work?
              </label>
              <div className="flex gap-3">
                {[
                  { value: true, label: 'Yes' },
                  { value: false, label: 'No' },
                ].map(({ value, label }) => (
                  <button
                    key={String(value)}
                    type="button"
                    onClick={() => setWouldUseAgain(value)}
                    className={`px-4 py-2 rounded border text-sm font-medium transition-colors ${
                      wouldUseAgain === value
                        ? 'border-green-600 bg-green-600 text-white'
                        : 'border-gray-300 text-gray-600 hover:border-green-400'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
                <AlertTriangle className="h-4 w-4 flex-shrink-0" />
                {error}
              </div>
            )}

            <Button
              type="submit"
              disabled={submit.isPending}
              className="w-full bg-green-700 hover:bg-green-800 text-white"
            >
              {submit.isPending ? 'Submitting...' : 'Submit Feedback'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
