// /** @odoo-module **/

$(document).ready(function () {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        height: 'auto',
        selectable: true,
        events: [],
        selectAllow: function (selectInfo) {
            const today = new Date();
            today.setHours(0, 0, 0, 0); // Normalize to start of day
            return selectInfo.start >= today; // Only allow today or future dates
        },
        dateClick: function (info) {    
            const clickedDate = info.date;
            const weekday = clickedDate.toLocaleDateString('en-US', { weekday: 'long' });
            const dateStr = info.dateStr;
            const slotContainer = $('#slot-list');
            slotContainer.empty();
    
            const now = new Date();
            const today = new Date();
            today.setHours(0, 0, 0, 0);
    
            // Prevent rendering slots for past dates
            if (clickedDate < today) {
                slotContainer.append('<p class="text-danger">Cannot select past dates.</p>');
                return;
            }
    
            const slots = window.weekdaySlots?.[weekday] || [];

            const booked = window.bookedSlotsByDate?.[dateStr] || [];
    
            // Convert "12:00 PM" to minutes for comparison
            function timeStrToMinutes(str) {
                const [time, modifier] = str.split(' ');
                let [hours, minutes] = time.split(':').map(Number);
    
                if (modifier === 'PM' && hours < 12) hours += 12;
                if (modifier === 'AM' && hours === 12) hours = 0;
    
                return hours * 60 + minutes;
            }
    
            // Convert "12:00 PM" to 24-hour format for ISO string
            function timeStrTo24Hour(str) {
                const [time, modifier] = str.split(' ');
                let [hours, minutes] = time.split(':').map(Number);
    
                if (modifier === 'PM' && hours < 12) hours += 12;
                if (modifier === 'AM' && hours === 12) hours = 0;
    
                return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:00`;
            }
    
            // Filter out booked slots and past slots (for current date)
            const availableSlots = slots.filter(slot => {
                const slotFromMin = timeStrToMinutes(slot.from);
                const slotToMin = timeStrToMinutes(slot.to);
    
                // For current date, skip slots where end time is in the past
                // if (dateStr === now.toISOString().split('T')[0]) {
                //     const slotDateTime = new Date(`${dateStr}T${timeStrTo24Hour(slot.to)}`);
                //     if (slotDateTime < now) {
                //         return false; // Skip past slots on current date
                //     }
                // }
    
                return !booked.some(b => {
                    const bookedFromMin = parseInt(b.from.split(':')[0]) * 60 + parseInt(b.from.split(':')[1]);
                    const bookedToMin = parseInt(b.to.split(':')[0]) * 60 + parseInt(b.to.split(':')[1]);
    
                    return (
                        (slotFromMin >= bookedFromMin && slotFromMin < bookedToMin) ||
                        (slotToMin > bookedFromMin && slotToMin <= bookedToMin) ||
                        (slotFromMin <= bookedFromMin && slotToMin >= bookedToMin)
                    );
                });
            });
    
            // Render available slots
            availableSlots.forEach(slot => {
                const slotDateTime = new Date(`${dateStr}T${timeStrTo24Hour(slot.from)}`);
                const isDisabled = dateStr === now.toISOString().split('T')[0] && slotDateTime < now;
            
                // Remove seconds from the time display
                const fromTime = timeStrTo24Hour(slot.from).slice(0, 5); // "HH:MM:00" -> "HH:MM"
                const toTime = timeStrTo24Hour(slot.to).slice(0, 5);     // "HH:MM:00" -> "HH:MM"
            
                const button = `
                    <div class="col-6 mb-2">
                        <button id="aginda" class="btn btn-outline-primary w-100"
                            data-from="${dateStr}T${timeStrTo24Hour(slot.from)}"
                            data-to="${dateStr}T${timeStrTo24Hour(slot.to)}"
                            data-doctor-id="${slot.doctor.id}"
                            ${window.app_id ? `data-app-id="${window.app_id}"` : ''}
                            ${isDisabled ? 'disabled' : ''}>
                            ${fromTime} - ${toTime}
                        </button>
                    </div>`;
                slotContainer.append(button);
            });
            // availableSlots.forEach(slot => {
            //     const slotDateTime = new Date(`${dateStr}T${timeStrTo24Hour(slot.from)}`);
            //     const isDisabled = dateStr === now.toISOString().split('T')[0] && slotDateTime < now;
    
            //     const button = `
            //         <div class="col-6 mb-2">
            //             <button id="aginda" class="btn btn-outline-primary w-100"
            //                 data-from="${dateStr}T${timeStrTo24Hour(slot.from)}"
            //                 data-to="${dateStr}T${timeStrTo24Hour(slot.to)}"
            //                 data-doctor-id="${slot.doctor.id}"
            //                 ${window.app_id ? `data-app-id="${window.app_id}"` : ''}
            //                 ${isDisabled ? 'disabled' : ''}>
            //                 ${slot.from}
            //             </button>
            //         </div>`;
            //     slotContainer.append(button);
            // });
    
            if (availableSlots.length === 0) {
                slotContainer.append('<p class="text-danger">No available slots for this date.</p>');
            }
        }

    });

    calendar.render();

    // ✅ Trigger today's date slot display
    const today = new Date();
    calendar.today(); // Navigate to today
    calendar.trigger('dateClick', {
        date: today,
        dateStr: today.toISOString().split('T')[0],
        allDay: true,
        dayEl: null, // not used
        jsEvent: null,
        view: calendar.view
    });


    $('#slot-list').on('click', '#aginda', async function () {
        const from = $(this).data('from');
        const to = $(this).data('to');
        const doctorId = $(this).data('doctor-id');
        const appId = $(this).data('app-id');
        if (appId) {
            window.location.href = `/edit_appointment?apt_id=${encodeURIComponent(appId)}&from_time=${encodeURIComponent(from)}&to_time=${encodeURIComponent(to)}&doctor_id=${doctorId}`;
        }else{
            window.location.href = `/my_appointment/new?from_time=${encodeURIComponent(from)}&to_time=${encodeURIComponent(to)}&doctor_id=${doctorId}`;

        }
        
        // window.location.href = `/my_appointment/new?from_time=${encodeURIComponent(from)}&to_time=${encodeURIComponent(to)}&doctor_id=${doctorId}`;


        
        
    });


   
});








