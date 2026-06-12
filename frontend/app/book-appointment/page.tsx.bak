'use client';
export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter, useSearchParams } from 'next/navigation';

interface Slot {
  time: string;
  available: boolean;
}

interface Doctor {
  id: number;
  name: string;
  specialization: string;
}

interface Hospital {
  id: number;
  name: string;
}

export default function BookAppointmentPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const hospitalId = searchParams.get('hospitalId');
  const doctorId = searchParams.get('doctorId');

  const [doctor, setDoctor] = useState<Doctor | null>(null);
  const [hospital, setHospital] = useState<Hospital | null>(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [slots, setSlots] = useState<Slot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [loading, setLoading] = useState(true);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchDoctorAndHospital();
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    setSelectedDate(tomorrow.toISOString().split('T')[0]);
  }, []);

  useEffect(() => {
    if (selectedDate) {
      fetchSlots();
    }
  }, [selectedDate]);

  const fetchDoctorAndHospital = async () => {
    try {
      const token = localStorage.getItem('token');
      const doctorRes = await axios.get(
        `http://localhost:8000/doctors/${doctorId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setDoctor(doctorRes.data);

      const hospitalRes = await axios.get(
        `http://localhost:8000/hospitals/${hospitalId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setHospital(hospitalRes.data);
    } catch (err: any) {
      setError('Failed to fetch doctor or hospital details');
    }
    setLoading(false);
  };

  const fetchSlots = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/appointments/slots/${doctorId}/${selectedDate}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const slotsData = response.data.slots || [];
      setSlots(slotsData);
      setSelectedSlot('');
    } catch (err: any) {
      setError('Failed to fetch slots');
    }
  };

  const handleBookAppointment = async () => {
    if (!selectedSlot) {
      setError('Please select a time slot');
      return;
    }

    setBookingLoading(true);
    setError('');
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        'http://localhost:8000/appointments/',
        {
          doctor_id: parseInt(doctorId!),
          hospital_id: parseInt(hospitalId!),
          appointment_date: selectedDate,
          appointment_time: selectedSlot,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSuccess('Appointment booked successfully!');
      setTimeout(() => {
        router.push('/dashboard');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to book appointment');
    }
    setBookingLoading(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-2xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">HealthBridge</h1>
          <button
            onClick={() => router.back()}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back
          </button>
        </div>
      </nav>

      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Book Appointment
          </h2>

          <div className="bg-indigo-50 rounded-lg p-6 mb-8">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Doctor</p>
                <p className="text-lg font-semibold text-gray-800">
                  {doctor?.name}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Specialization</p>
                <p className="text-lg font-semibold text-gray-800">
                  {doctor?.specialization}
                </p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-600">Hospital</p>
                <p className="text-lg font-semibold text-gray-800">
                  {hospital?.name}
                </p>
              </div>
            </div>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
              {success}
            </div>
          )}

          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Date
            </label>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              min={new Date().toISOString().split('T')[0]}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
            />
          </div>

          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Time Slot
            </label>
            <div className="grid grid-cols-4 gap-2">
              {slots.length > 0 ? (
                slots.map((slot) => (
                  <button
                    key={slot.time}
                    onClick={() => slot.available && setSelectedSlot(slot.time)}
                    disabled={!slot.available}
                    className={`py-2 px-3 rounded font-semibold transition ${
                      selectedSlot === slot.time
                        ? 'bg-indigo-600 text-white'
                        : slot.available
                        ? 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                        : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    {slot.time}
                  </button>
                ))
              ) : (
                <p className="text-gray-600 col-span-4">
                  No slots available for this date
                </p>
              )}
            </div>
          </div>

          <button
            onClick={handleBookAppointment}
            disabled={bookingLoading || !selectedSlot}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400"
          >
            {bookingLoading ? 'Booking...' : 'Confirm Appointment'}
          </button>
        </div>
      </div>
    </div>
  );
}