'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface Appointment {
  id: number;
  doctor_id: number;
  doctor_name: string;
  hospital_id: number;
  hospital_name: string;
  appointment_date: string;
  appointment_time: string;
  status: string;
}

export default function Dashboard() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/');
        return;
      }
      
      const response = await axios.get(
        'http://localhost:8000/appointments/',
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const data = Array.isArray(response.data)
        ? response.data
        : response.data.appointments || [];
      setAppointments(data);
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || 'Failed to fetch appointments');
    }
    setLoading(false);
  };

  const handleCancel = async (appointmentId: number) => {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `http://localhost:8000/appointments/${appointmentId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAppointments(appointments.filter(a => a.id !== appointmentId));
      alert('Appointment cancelled successfully');
    } catch (err: any) {
      alert('Failed to cancel appointment');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/');
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">HealthBridge</h1>
          <div className="flex gap-4">
            <Link
              href="/hospitals"
              className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 font-semibold"
            >
              Book New Appointment
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
        <h2 className="text-3xl font-bold text-gray-800 mb-8">My Appointments</h2>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {loading ? (
          <p className="text-gray-600">Loading appointments...</p>
        ) : appointments.length > 0 ? (
          <div className="space-y-4">
            {appointments.map((appointment) => (
              <div
                key={appointment.id}
                className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition"
              >
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-600">Doctor</p>
                    <p className="text-lg font-semibold text-gray-800">
                      {appointment.doctor_name}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Hospital</p>
                    <p className="text-lg font-semibold text-gray-800">
                      {appointment.hospital_name}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Date</p>
                    <p className="text-lg font-semibold text-gray-800">
                      {formatDate(appointment.appointment_date)}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Time</p>
                    <p className="text-lg font-semibold text-gray-800">
                      {appointment.appointment_time}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      appointment.status === 'confirmed'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}
                  >
                    {appointment.status}
                  </span>
                  <button
                    onClick={() => handleCancel(appointment.id)}
                    className="ml-auto bg-red-100 text-red-700 px-4 py-2 rounded hover:bg-red-200 font-semibold"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 mb-4">No appointments booked yet</p>
            <Link
              href="/hospitals"
              className="inline-block bg-indigo-600 text-white px-6 py-2 rounded hover:bg-indigo-700 font-semibold"
            >
              Book Your First Appointment
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
