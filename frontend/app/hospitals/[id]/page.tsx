'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';

interface Hospital {
  id: number;
  name: string;
  city: string;
  address: string;
  phone: string;
}

interface Doctor {
  id: number;
  name: string;
  specialization: string;
  experience_years: number;
  consultation_fee: number;
  hospital_id: number;
}

export default function HospitalDetail() {
  const params = useParams();
  const hospitalId = params.id as string;
  const [hospital, setHospital] = useState<Hospital | null>(null);
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    fetchHospitalAndDoctors();
  }, [hospitalId]);

  const fetchHospitalAndDoctors = async () => {
    try {
      const token = localStorage.getItem('token');
      const hospitalRes = await axios.get(
        `http://localhost:8000/hospitals/${hospitalId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setHospital(hospitalRes.data);

      const doctorsRes = await axios.get(
        `http://localhost:8000/doctors/?hospital_id=${hospitalId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const doctorsData = Array.isArray(doctorsRes.data)
        ? doctorsRes.data
        : doctorsRes.data.doctors || [];
      setDoctors(doctorsData);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || 'Failed to fetch data');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  if (loading) {
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
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">HealthBridge</h1>
          <div className="flex gap-4">
            <Link
              href="/hospitals"
              className="text-gray-600 hover:text-gray-900"
            >
              Back to Hospitals
            </Link>
            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {hospital && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              {hospital.name}
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">City</p>
                <p className="text-lg font-semibold text-gray-800">
                  {hospital.city}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="text-lg font-semibold text-gray-800">
                  {hospital.phone}
                </p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-600">Address</p>
                <p className="text-lg font-semibold text-gray-800">
                  {hospital.address}
                </p>
              </div>
            </div>
          </div>
        )}

        <h3 className="text-2xl font-bold text-gray-800 mb-6">Available Doctors</h3>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {doctors && doctors.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {doctors.map((doctor) => (
              <div
                key={doctor.id}
                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
              >
                <h4 className="text-xl font-bold text-gray-800 mb-2">
                  {doctor.name}
                </h4>
                <p className="text-indigo-600 font-semibold mb-2">
                  {doctor.specialization}
                </p>
                <div className="space-y-2 mb-4">
                  <p className="text-sm text-gray-600">
                    <span className="font-semibold">Experience:</span>{' '}
                    {doctor.experience_years} years
                  </p>
                  <p className="text-sm text-gray-600">
                    <span className="font-semibold">Consultation Fee:</span> ₹
                    {doctor.consultation_fee}
                  </p>
                </div>
                <Link
                  href={`/book-appointment?hospitalId=${hospitalId}&doctorId=${doctor.id}`}
                  className="w-full block text-center bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 font-semibold"
                >
                  Book Appointment
                </Link>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">No doctors found for this hospital</p>
        )}
      </div>
    </div>
  );
}
