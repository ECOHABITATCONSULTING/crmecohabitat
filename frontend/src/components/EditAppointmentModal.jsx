import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { X, Save, Trash2, Calendar as CalendarIcon, Clock, User, Briefcase, FileText } from 'lucide-react';
import styles from './AddAppointmentModal.module.css';

const EditAppointmentModal = ({ appointment, onClose, onSuccess, onDelete }) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    date: '',
    time: '',
    title: '',
    commercial_id: null,
    user_id: null
  });
  const [comment, setComment] = useState('');
  const [commerciaux, setCommerciaux] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const isOwner = user?.role === 'admin' || appointment?.user_id === user?.id;
  const isReadOnly = !isOwner;

  useEffect(() => {
    if (appointment) {
      setFormData({
        date: appointment.date,
        time: appointment.time,
        title: appointment.title,
        commercial_id: appointment.commercial_id || null,
        user_id: appointment.user_id
      });
    }
    fetchCommerciaux();
    if (user?.role === 'admin') {
      fetchAgents();
    }
  }, [appointment]);

  const fetchCommerciaux = async () => {
    try {
      const response = await api.get('/commerciaux');
      setCommerciaux(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des commerciaux:', error);
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

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.date || !formData.time || !formData.title) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.patch(`/appointments/${appointment.id}`, formData);

      // Add comment if provided
      if (comment.trim()) {
        const contactId = appointment.client_id || appointment.lead_id;
        const endpoint = appointment.client_id ? `/clients/${contactId}/comments` : `/leads/${contactId}/comments`;
        await api.post(endpoint, { content: comment });
      }

      onSuccess();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la modification');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce rendez-vous ?')) {
      return;
    }

    try {
      await api.delete(`/appointments/${appointment.id}`);
      onDelete();
    } catch (err) {
      setError(err.response?.data?.error || 'Erreur lors de la suppression');
    }
  };

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>
            <CalendarIcon size={24} /> Modifier le rendez-vous
          </h2>
          <button onClick={onClose} className={styles.closeBtn}>
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        {isReadOnly && (
          <div className={styles.warning}>
            ⚠️ Ce rendez-vous appartient à {appointment.username}. Vous pouvez le consulter mais pas le modifier.
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Contact info (read-only) */}
          <div className={styles.infoSection}>
            <h3 className={styles.sectionTitle}>Contact</h3>
            <div className={styles.contactInfo}>
              <strong>{appointment.first_name} {appointment.last_name}</strong>
              {appointment.postal_code && <span> • {appointment.postal_code}</span>}
              <div className={styles.contactType}>
                {appointment.client_id ? '(Client)' : '(Lead)'}
              </div>
            </div>
          </div>

          {/* Date */}
          <div className={styles.formGroup}>
            <label className={styles.label}>
              <CalendarIcon size={18} /> Date *
            </label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              className={styles.input}
              disabled={isReadOnly}
              required
            />
          </div>

          {/* Time */}
          <div className={styles.formGroup}>
            <label className={styles.label}>
              <Clock size={18} /> Heure *
            </label>
            <input
              type="time"
              value={formData.time}
              onChange={(e) => setFormData({ ...formData, time: e.target.value })}
              className={styles.input}
              disabled={isReadOnly}
              required
            />
          </div>

          {/* Title */}
          <div className={styles.formGroup}>
            <label className={styles.label}>
              <FileText size={18} /> Titre *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className={styles.input}
              disabled={isReadOnly}
              placeholder="Titre du rendez-vous"
              required
            />
          </div>

          {/* Agent (admin only) */}
          {user?.role === 'admin' && (
            <div className={styles.formGroup}>
              <label className={styles.label}>
                <User size={18} /> Agent
              </label>
              <select
                value={formData.user_id || ''}
                onChange={(e) => setFormData({ ...formData, user_id: parseInt(e.target.value) || null })}
                className={styles.input}
              >
                <option value="">Sélectionner un agent</option>
                {agents.map(agent => (
                  <option key={agent.id} value={agent.id}>{agent.username}</option>
                ))}
              </select>
            </div>
          )}

          {/* Commercial */}
          <div className={styles.formGroup}>
            <label className={styles.label}>
              <Briefcase size={18} /> Commercial
            </label>
            <select
              value={formData.commercial_id || ''}
              onChange={(e) => setFormData({ ...formData, commercial_id: parseInt(e.target.value) || null })}
              className={styles.input}
              disabled={isReadOnly}
            >
              <option value="">Aucun</option>
              {commerciaux.map(commercial => (
                <option key={commercial.id} value={commercial.id}>{commercial.name}</option>
              ))}
            </select>
          </div>

          {/* Comment */}
          <div className={styles.formGroup}>
            <label className={styles.label}>
              <FileText size={18} /> Ajouter un commentaire
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className={styles.textarea}
              disabled={isReadOnly}
              placeholder="Commentaire optionnel..."
              rows={3}
            />
          </div>

          {/* Actions */}
          <div className={styles.formActions}>
            {isOwner && (
              <button
                type="button"
                onClick={handleDelete}
                className={styles.deleteBtn}
              >
                <Trash2 size={18} /> Supprimer
              </button>
            )}
            <div className={styles.rightActions}>
              <button type="button" onClick={onClose} className={styles.cancelBtn}>
                {isReadOnly ? 'Fermer' : 'Annuler'}
              </button>
              {isOwner && (
                <button type="submit" className={styles.submitBtn} disabled={loading}>
                  <Save size={18} /> {loading ? 'Enregistrement...' : 'Enregistrer'}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditAppointmentModal;
