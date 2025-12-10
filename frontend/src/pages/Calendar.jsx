import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import frLocale from '@fullcalendar/core/locales/fr';
import { Plus, User, Briefcase } from 'lucide-react';
import styles from './Calendar.module.css';
import AddAppointmentModal from '../components/AddAppointmentModal';
import EditAppointmentModal from '../components/EditAppointmentModal';

const Calendar = () => {
  const { user } = useAuth();
  const calendarRef = useRef(null);
  const [appointments, setAppointments] = useState([]);
  const [events, setEvents] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [selectedCommercial, setSelectedCommercial] = useState(''); // PHASE 3.3
  const [agents, setAgents] = useState([]);
  const [commerciaux, setCommerciaux] = useState([]); // PHASE 3.3

  useEffect(() => {
    fetchAppointments();
    if (user?.role === 'admin') {
      fetchAgents();
    }
    fetchCommerciaux(); // PHASE 3.3
  }, []);

  useEffect(() => {
    // Convert appointments to FullCalendar events
    // PHASE 3.3 - Filter by agent AND/OR commercial
    const calendarEvents = appointments
      .filter(apt => {
        const agentMatch = !selectedAgent || apt.user_id === parseInt(selectedAgent);
        const commercialMatch = !selectedCommercial || apt.commercial_id === parseInt(selectedCommercial);
        return agentMatch && commercialMatch;
      })
      .map(apt => {
        // Build rich title with postal_code and commercial
        const parts = [
          `${apt.first_name} ${apt.last_name}`,
        ];

        if (apt.postal_code) {
          parts.push(apt.postal_code);
        }

        if (apt.commercial_name) {
          parts.push(`👤 ${apt.commercial_name}`);
        }

        const title = `${apt.time} - ${parts.join(' • ')}`;

        return {
          id: apt.id,
          title: title,
          start: `${apt.date}T${apt.time}`,
          extendedProps: {
            leadName: `${apt.first_name} ${apt.last_name}`,
            agent: apt.username,
            time: apt.time,
            leadId: apt.lead_id,
            clientId: apt.client_id,
            postalCode: apt.postal_code,
            commercialName: apt.commercial_name,
            commercialColor: apt.commercial_color
          },
          backgroundColor: apt.commercial_color || getEventColor(apt.user_id),
          borderColor: apt.commercial_color || getEventColor(apt.user_id)
        };
      });
    setEvents(calendarEvents);
  }, [appointments, selectedAgent, selectedCommercial]); // PHASE 3.3

  const fetchAppointments = async () => {
    try {
      const response = await api.get('/appointments');
      setAppointments(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des RDV:', error);
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await api.get('/users/agents');
      setAgents(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des agents:', error);
    }
  };

  // PHASE 3.3 - Fetch commerciaux for filter
  const fetchCommerciaux = async () => {
    try {
      const response = await api.get('/commerciaux');
      setCommerciaux(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des commerciaux:', error);
    }
  };

  const getEventColor = (userId) => {
    const colors = ['#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6', '#06b6d4'];
    return colors[userId % colors.length];
  };

  const handleEventDrop = async (info) => {
    try {
      // PHASE 3.4 - Permission check: agents can only drag their own appointments
      const appointment = appointments.find(apt => apt.id === parseInt(info.event.id));
      if (user?.role === 'agent' && appointment && appointment.user_id !== user.id) {
        info.revert();
        alert('Vous ne pouvez déplacer que vos propres rendez-vous');
        return;
      }

      const newDate = info.event.start.toISOString().split('T')[0];
      const newTime = info.event.start.toTimeString().slice(0, 5);

      await api.patch(`/appointments/${info.event.id}`, {
        date: newDate,
        time: newTime
      });

      fetchAppointments();
    } catch (error) {
      console.error('Erreur lors du déplacement du RDV:', error);
      info.revert();
      alert('Erreur lors du déplacement du rendez-vous');
    }
  };

  const handleEventClick = (info) => {
    const event = info.event;
    const appointmentId = parseInt(event.id);
    const appointment = appointments.find(apt => apt.id === appointmentId);

    if (appointment) {
      setSelectedAppointment(appointment);
      setShowEditModal(true);
    }
  };

  const handleDeleteAppointment = async (id) => {
    try {
      await api.delete(`/appointments/${id}`);
      fetchAppointments();
    } catch (error) {
      console.error('Erreur lors de la suppression:', error);
      alert('Erreur lors de la suppression du rendez-vous');
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>Agenda</h1>
        <div className={styles.toolbar}>
          {user?.role === 'admin' && (
            <div className={styles.filterGroup}>
              <User size={18} />
              <select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                className={styles.agentFilter}
              >
                <option value="">Tous les agents</option>
                {agents.map(agent => (
                  <option key={agent.id} value={agent.id}>{agent.username}</option>
                ))}
              </select>
            </div>
          )}
          {/* PHASE 3.3 - Commercial filter */}
          <div className={styles.filterGroup}>
            <Briefcase size={18} />
            <select
              value={selectedCommercial}
              onChange={(e) => setSelectedCommercial(e.target.value)}
              className={styles.commercialFilter}
            >
              <option value="">Tous les commerciaux</option>
              {commerciaux.map(commercial => (
                <option key={commercial.id} value={commercial.id}>{commercial.name}</option>
              ))}
            </select>
          </div>
          <button onClick={() => setShowAddModal(true)} className={styles.addBtn}>
            <Plus size={20} /> Ajouter RDV
          </button>
        </div>
      </div>

      <div className={styles.calendarWrapper}>
        <FullCalendar
          ref={calendarRef}
          plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
          initialView="timeGridWeek"
          locale={frLocale}
          headerToolbar={{
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
          }}
          buttonText={{
            today: "Aujourd'hui",
            month: 'Mois',
            week: 'Semaine',
            day: 'Jour'
          }}
          slotMinTime="08:00:00"
          slotMaxTime="22:00:00"
          allDaySlot={false}
          height="auto"
          events={events}
          editable={true}
          droppable={true}
          eventDrop={handleEventDrop}
          eventClick={handleEventClick}
          eventTimeFormat={{
            hour: '2-digit',
            minute: '2-digit',
            meridiem: false
          }}
          slotLabelFormat={{
            hour: '2-digit',
            minute: '2-digit',
            meridiem: false
          }}
          weekends={true}
          firstDay={1}
        />
      </div>

      {showAddModal && (
        <AddAppointmentModal
          onClose={() => setShowAddModal(false)}
          onSuccess={() => {
            fetchAppointments();
            setShowAddModal(false);
          }}
        />
      )}

      {showEditModal && selectedAppointment && (
        <EditAppointmentModal
          appointment={selectedAppointment}
          onClose={() => {
            setShowEditModal(false);
            setSelectedAppointment(null);
          }}
          onSuccess={() => {
            fetchAppointments();
            setShowEditModal(false);
            setSelectedAppointment(null);
          }}
          onDelete={() => {
            fetchAppointments();
            setShowEditModal(false);
            setSelectedAppointment(null);
          }}
        />
      )}
    </div>
  );
};

export default Calendar;
