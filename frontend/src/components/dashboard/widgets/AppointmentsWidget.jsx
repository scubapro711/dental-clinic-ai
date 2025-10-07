/**
 * Appointments Widget - Today's appointments with Sophia integration
 * 
 * Architecture:
 * - Display: Widget → API → Database (direct)
 * - Actions: Widget → API → LangGraph → Sophia Agent → Tools
 * 
 * Displays:
 * - Today's appointments list
 * - Patient info, time, treatment
 * - Status badges
 * - Action buttons (Reschedule, Cancel) that call Sophia
 */

import { useEffect, useState } from 'react'
import { Widget } from '../Widget'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Calendar, Clock, User, Phone, AlertCircle, RotateCw, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"

export function AppointmentsWidget() {
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [actionLoading, setActionLoading] = useState({})
  
  // Reschedule dialog state
  const [rescheduleDialog, setRescheduleDialog] = useState({
    open: false,
    appointment: null,
    newDate: '',
    newTime: '',
    reason: ''
  })
  
  // Cancel dialog state
  const [cancelDialog, setCancelDialog] = useState({
    open: false,
    appointment: null,
    reason: ''
  })

  useEffect(() => {
    loadAppointments()
    
    // Refresh every 30 seconds
    const interval = setInterval(loadAppointments, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadAppointments = async () => {
    try {
      // Architecture: Widget → API → Database (direct query, no LangGraph)
      const data = await api.get('/dashboard/appointments/today')
      setAppointments(data.appointments || [])
      setError(null)
      
      console.log('[AppointmentsWidget] Loaded', data.appointments?.length, 'appointments')
    } catch (err) {
      console.error('Error loading appointments:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleReschedule = (appointment) => {
    // Open reschedule dialog
    setRescheduleDialog({
      open: true,
      appointment,
      newDate: appointment.date,
      newTime: appointment.time,
      reason: ''
    })
  }

  const confirmReschedule = async () => {
    const { appointment, newDate, newTime, reason } = rescheduleDialog
    
    if (!newDate || !newTime || !reason) {
      alert('Please fill in all fields')
      return
    }
    
    setActionLoading({ ...actionLoading, [appointment.id]: 'reschedule' })
    
    try {
      // Architecture: Widget → API → LangGraph → Sophia Agent
      // Send natural language command to Sophia
      const message = `Reschedule appointment ${appointment.id} to ${newDate} at ${newTime}. Reason: ${reason}`
      
      const response = await api.sendMessage(message)
      
      console.log('[AppointmentsWidget] Reschedule response:', response)
      
      // Close dialog
      setRescheduleDialog({ open: false, appointment: null, newDate: '', newTime: '', reason: '' })
      
      // Reload appointments
      await loadAppointments()
      
      // Show success message
      alert('Appointment rescheduled successfully!')
      
    } catch (err) {
      console.error('Error rescheduling appointment:', err)
      alert('Failed to reschedule appointment: ' + err.message)
    } finally {
      setActionLoading({ ...actionLoading, [appointment.id]: null })
    }
  }

  const handleCancel = (appointment) => {
    // Open cancel dialog
    setCancelDialog({
      open: true,
      appointment,
      reason: ''
    })
  }

  const confirmCancel = async () => {
    const { appointment, reason } = cancelDialog
    
    if (!reason) {
      alert('Please provide a reason for cancellation')
      return
    }
    
    setActionLoading({ ...actionLoading, [appointment.id]: 'cancel' })
    
    try {
      // Architecture: Widget → API → LangGraph → Sophia Agent
      // Send natural language command to Sophia
      const message = `Cancel appointment ${appointment.id}. Reason: ${reason}. Notify the patient.`
      
      const response = await api.sendMessage(message)
      
      console.log('[AppointmentsWidget] Cancel response:', response)
      
      // Close dialog
      setCancelDialog({ open: false, appointment: null, reason: '' })
      
      // Reload appointments
      await loadAppointments()
      
      // Show success message
      alert('Appointment cancelled successfully!')
      
    } catch (err) {
      console.error('Error cancelling appointment:', err)
      alert('Failed to cancel appointment: ' + err.message)
    } finally {
      setActionLoading({ ...actionLoading, [appointment.id]: null })
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800'
      case 'scheduled':
        return 'bg-blue-100 text-blue-800'
      case 'completed':
        return 'bg-gray-100 text-gray-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      case 'no_show':
        return 'bg-orange-100 text-orange-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <>
      <Widget
        id="appointments"
        title="Today's Appointments"
        icon={Calendar}
        loading={loading}
        error={error}
        empty={appointments.length === 0}
        emptyMessage="No appointments today"
        onRefresh={loadAppointments}
      >
        <div className="space-y-2">
          {appointments.map((appointment) => (
            <div
              key={appointment.id}
              className="p-3 border rounded-lg hover:shadow-sm transition-shadow"
            >
              {/* Appointment Header */}
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">{appointment.time}</span>
                  <Badge className={cn('text-xs', getStatusColor(appointment.status))}>
                    {appointment.status}
                  </Badge>
                </div>
              </div>

              {/* Patient Info */}
              <div className="space-y-1 mb-3">
                <div className="flex items-center gap-2 text-sm">
                  <User className="h-3 w-3 text-muted-foreground" />
                  <span className="font-medium">{appointment.patient_name}</span>
                </div>
                {appointment.patient_phone && (
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Phone className="h-3 w-3" />
                    <span>{appointment.patient_phone}</span>
                  </div>
                )}
                {appointment.treatment && (
                  <div className="text-xs text-muted-foreground">
                    Treatment: {appointment.treatment}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              {appointment.status !== 'completed' && appointment.status !== 'cancelled' && (
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleReschedule(appointment)}
                    disabled={actionLoading[appointment.id] === 'reschedule'}
                    className="h-7 text-xs"
                  >
                    <RotateCw className="h-3 w-3 mr-1" />
                    Reschedule
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleCancel(appointment)}
                    disabled={actionLoading[appointment.id] === 'cancel'}
                    className="h-7 text-xs text-destructive hover:text-destructive"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Cancel
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      </Widget>

      {/* Reschedule Dialog */}
      <Dialog open={rescheduleDialog.open} onOpenChange={(open) => setRescheduleDialog({ ...rescheduleDialog, open })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reschedule Appointment</DialogTitle>
            <DialogDescription>
              Rescheduling appointment for {rescheduleDialog.appointment?.patient_name}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="new-date">New Date</Label>
              <Input
                id="new-date"
                type="date"
                value={rescheduleDialog.newDate}
                onChange={(e) => setRescheduleDialog({ ...rescheduleDialog, newDate: e.target.value })}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="new-time">New Time</Label>
              <Input
                id="new-time"
                type="time"
                value={rescheduleDialog.newTime}
                onChange={(e) => setRescheduleDialog({ ...rescheduleDialog, newTime: e.target.value })}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="reason">Reason</Label>
              <Textarea
                id="reason"
                placeholder="Why are you rescheduling this appointment?"
                value={rescheduleDialog.reason}
                onChange={(e) => setRescheduleDialog({ ...rescheduleDialog, reason: e.target.value })}
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setRescheduleDialog({ open: false, appointment: null, newDate: '', newTime: '', reason: '' })}
            >
              Cancel
            </Button>
            <Button onClick={confirmReschedule}>
              Confirm Reschedule
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Cancel Dialog */}
      <Dialog open={cancelDialog.open} onOpenChange={(open) => setCancelDialog({ ...cancelDialog, open })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel Appointment</DialogTitle>
            <DialogDescription>
              Cancelling appointment for {cancelDialog.appointment?.patient_name}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="cancel-reason">Reason for Cancellation</Label>
              <Textarea
                id="cancel-reason"
                placeholder="Why are you cancelling this appointment?"
                value={cancelDialog.reason}
                onChange={(e) => setCancelDialog({ ...cancelDialog, reason: e.target.value })}
              />
            </div>
            
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <AlertCircle className="h-4 w-4" />
              <span>The patient will be notified about the cancellation.</span>
            </div>
          </div>
          
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCancelDialog({ open: false, appointment: null, reason: '' })}
            >
              Go Back
            </Button>
            <Button variant="destructive" onClick={confirmCancel}>
              Confirm Cancellation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
