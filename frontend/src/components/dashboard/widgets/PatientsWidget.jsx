/**
 * Patients Widget - Quick patient lookup and info
 * 
 * Architecture: Widget → API → Database (Mock Odoo)
 * 
 * Displays:
 * - Recent patients
 * - Search functionality
 * - Quick patient info
 * - Links to conversations and appointments
 */

import { useEffect, useState } from 'react'
import { Widget } from '../Widget'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { User, Phone, Mail, Calendar, MessageSquare, Search } from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api'

export function PatientsWidget() {
  const [patients, setPatients] = useState([])
  const [filteredPatients, setFilteredPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadPatients()
  }, [])

  useEffect(() => {
    // Filter patients based on search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      const filtered = patients.filter(patient =>
        patient.name.toLowerCase().includes(query) ||
        patient.phone?.toLowerCase().includes(query) ||
        patient.email?.toLowerCase().includes(query)
      )
      setFilteredPatients(filtered)
    } else {
      setFilteredPatients(patients)
    }
  }, [searchQuery, patients])

  const loadPatients = async () => {
    try {
      // Architecture: Widget → API → Mock Odoo
      // For now, use mock data
      // TODO: Create proper patients API endpoint
      
      const mockPatients = [
        {
          id: 'patient_001',
          name: 'John Doe',
          phone: '+1-555-0101',
          email: 'john.doe@example.com',
          last_visit: '2025-10-01',
          next_appointment: '2025-10-15',
          status: 'active',
          total_visits: 12,
        },
        {
          id: 'patient_002',
          name: 'Jane Smith',
          phone: '+1-555-0102',
          email: 'jane.smith@example.com',
          last_visit: '2025-09-28',
          next_appointment: null,
          status: 'active',
          total_visits: 8,
        },
        {
          id: 'patient_003',
          name: 'Bob Johnson',
          phone: '+1-555-0103',
          email: 'bob.j@example.com',
          last_visit: '2025-10-03',
          next_appointment: '2025-10-10',
          status: 'active',
          total_visits: 15,
        },
        {
          id: 'patient_004',
          name: 'Alice Williams',
          phone: '+1-555-0104',
          email: 'alice.w@example.com',
          last_visit: '2025-09-15',
          next_appointment: null,
          status: 'inactive',
          total_visits: 3,
        },
        {
          id: 'patient_005',
          name: 'Charlie Brown',
          phone: '+1-555-0105',
          email: 'charlie.b@example.com',
          last_visit: '2025-10-02',
          next_appointment: '2025-10-20',
          status: 'active',
          total_visits: 20,
        },
      ]
      
      setPatients(mockPatients)
      setFilteredPatients(mockPatients)
      setError(null)
      
      console.log('[PatientsWidget] Loaded', mockPatients.length, 'patients')
    } catch (err) {
      console.error('Error loading patients:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <Widget
      id="patients"
      title="Patients"
      icon={User}
      loading={loading}
      error={error}
      empty={filteredPatients.length === 0}
      emptyMessage={searchQuery ? 'No patients found' : 'No patients'}
      onRefresh={loadPatients}
    >
      <div className="space-y-3">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search patients..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 h-8 text-sm"
          />
        </div>

        {/* Patients List */}
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {filteredPatients.map((patient) => (
            <div
              key={patient.id}
              className="p-3 border rounded-lg hover:shadow-sm transition-shadow"
            >
              {/* Patient Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{patient.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {patient.total_visits} visits
                    </p>
                  </div>
                </div>
                <Badge
                  variant={patient.status === 'active' ? 'default' : 'secondary'}
                  className="text-xs"
                >
                  {patient.status}
                </Badge>
              </div>

              {/* Contact Info */}
              <div className="space-y-1 mb-2">
                {patient.phone && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Phone className="h-3 w-3" />
                    <span>{patient.phone}</span>
                  </div>
                )}
                {patient.email && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Mail className="h-3 w-3" />
                    <span className="truncate">{patient.email}</span>
                  </div>
                )}
              </div>

              {/* Visit Info */}
              <div className="grid grid-cols-2 gap-2 text-xs mb-2">
                <div>
                  <p className="text-muted-foreground">Last Visit</p>
                  <p className="font-medium">{formatDate(patient.last_visit)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Next Appt</p>
                  <p className="font-medium">{formatDate(patient.next_appointment)}</p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                >
                  <MessageSquare className="h-3 w-3 mr-1" />
                  Chat
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  className="h-7 text-xs"
                >
                  <Calendar className="h-3 w-3 mr-1" />
                  Schedule
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        {!searchQuery && (
          <div className="pt-2 border-t text-xs text-muted-foreground text-center">
            Showing {filteredPatients.length} patients
          </div>
        )}
      </div>
    </Widget>
  )
}
