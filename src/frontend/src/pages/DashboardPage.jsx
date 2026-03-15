import React, { useState } from 'react';

import { Sidebar } from '../components/common/Sidebar.jsx';
import { UploadSection } from '../components/features/UploadSection.jsx';
import { TrainingHistoryChart } from '../components/features/TrainingHistoryChart.jsx';
import { ClassDistributionChart } from '../components/features/ClassDistributionChart.jsx';
import { TopClassesChart } from '../components/features/TopClassesChart.jsx';
import { PredictionResultsChart } from '../components/features/PredictionResultsChart.jsx';

export function DashboardPage() {
  const [uploadKey, setUploadKey] = useState(0);

  const handleUploadComplete = () => {
    setUploadKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <Sidebar />
      <main className="ml-56 p-8">
        <h2 className="text-lg font-semibold text-neutral-900 mb-6">Дашборд</h2>
        <div className="flex flex-col gap-6">
          <UploadSection onUploadComplete={handleUploadComplete} />
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <TrainingHistoryChart />
            <ClassDistributionChart />
            <PredictionResultsChart key={uploadKey} />
            <TopClassesChart />
          </div>
        </div>
      </main>
    </div>
  );
}
