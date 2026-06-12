'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Hospital {
  id: number;
  name: string;
  city: string;
  address: string;
  phone: string;
}

export default function Hospitals() {
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    fetchHospitals();
  }, []);

  const fetchHospitals = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('http://localhost:8000/hospitals/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      // Handle both array and object responses
      const data = Array.isArray(response.data) ? response.data : response.data.hospitals || [];
      setHospitals(data);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || 'Failed to fetch hospitals');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">HealthBridge</h1>
          <button
            onClick={handleLogout}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <h2 className="text-3xl font-bold mb-8">Find Hospitals</h2>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-gray-600">Loading hospitals...</p>
        ) : hospitals && hospitals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {hospitals.map((hospital: Hospital) => (
              <div
                key={hospital.id}
                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
              >
                <h3 className="text-xl font-bold text-gray-800 mb-2">
                  {hospital.name}
                </h3>
                <p className="text-gray-600 mb-2">{hospital.city}</p>
                <p className="text-sm text-gray-500 mb-4">{hospital.address}</p>
                <p className="text-sm font-semibold text-indigo-600 mb-4">
                  {hospital.phone}
                </p>
                <Link
                  href={`/hospitals/${hospital.id}`}
                  className="inline-block bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 text-sm font-semibold"
                >
                  View Doctors
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No hospitals found</p>
        )}
      </div>
    </div>
  );
}
