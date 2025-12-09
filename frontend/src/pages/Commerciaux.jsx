import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { Plus, Edit2, Trash2, RefreshCw, Briefcase } from 'lucide-react';
import styles from './Commerciaux.module.css';

const Commerciaux = () => {
  const { user } = useAuth();
  const [commerciaux, setCommerciaux] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    color: '#10b981'
  });

  useEffect(() => {
    fetchCommerciaux();
  }, []);

  const fetchCommerciaux = async () => {
    try {
      setLoading(true);
      const response = await api.get('/commerciaux');
      setCommerciaux(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement des commerciaux:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      alert('Le nom est obligatoire');
      return;
    }

    try {
      if (editingId) {
        await api.patch(`/commerciaux/${editingId}`, formData);
      } else {
        await api.post('/commerciaux', formData);
      }

      setFormData({ name: '', color: '#10b981' });
      setEditingId(null);
      setShowForm(false);
      fetchCommerciaux();
    } catch (error) {
      alert(error.response?.data?.error || 'Erreur lors de la sauvegarde');
    }
  };

  const handleEdit = (commercial) => {
    setFormData({
      name: commercial.name,
      color: commercial.color
    });
    setEditingId(commercial.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Supprimer ce commercial ?')) return;

    try {
      await api.delete(`/commerciaux/${id}`);
      fetchCommerciaux();
    } catch (error) {
      alert(error.response?.data?.error || 'Erreur lors de la suppression');
    }
  };

  const handleCancel = () => {
    setFormData({ name: '', color: '#10b981' });
    setEditingId(null);
    setShowForm(false);
  };

  if (user?.role !== 'admin') {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          Accès réservé aux administrateurs
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>
            <Briefcase size={32} /> Gestion des Commerciaux
          </h1>
          <p className={styles.subtitle}>
            {commerciaux.length} commercial(aux) enregistré(s)
          </p>
        </div>
        <div className={styles.headerActions}>
          <button onClick={fetchCommerciaux} className={styles.iconBtn} title="Rafraîchir">
            <RefreshCw size={18} />
          </button>
          {!showForm && (
            <button onClick={() => setShowForm(true)} className={styles.addBtn}>
              <Plus size={20} /> Ajouter un commercial
            </button>
          )}
        </div>
      </div>

      {showForm && (
        <div className={styles.formCard}>
          <h3 className={styles.formTitle}>
            {editingId ? 'Modifier le commercial' : 'Nouveau commercial'}
          </h3>
          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGroup}>
              <label className={styles.label}>Nom *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Nom du commercial"
                className={styles.input}
                required
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label}>Couleur</label>
              <div className={styles.colorPicker}>
                <input
                  type="color"
                  value={formData.color}
                  onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                  className={styles.colorInput}
                />
                <span className={styles.colorValue}>{formData.color}</span>
              </div>
            </div>

            <div className={styles.formActions}>
              <button type="button" onClick={handleCancel} className={styles.cancelBtn}>
                Annuler
              </button>
              <button type="submit" className={styles.submitBtn}>
                {editingId ? 'Mettre à jour' : 'Créer'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className={styles.tableContainer}>
        {loading ? (
          <div className={styles.loading}>Chargement...</div>
        ) : commerciaux.length === 0 ? (
          <div className={styles.empty}>
            Aucun commercial enregistré. Cliquez sur "Ajouter un commercial" pour commencer.
          </div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Couleur</th>
                <th>Nom</th>
                <th>Date de création</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {commerciaux.map(commercial => (
                <tr key={commercial.id}>
                  <td>
                    <div
                      className={styles.colorBadge}
                      style={{ backgroundColor: commercial.color }}
                    />
                  </td>
                  <td className={styles.name}>{commercial.name}</td>
                  <td className={styles.date}>
                    {new Date(commercial.created_at).toLocaleDateString('fr-FR')}
                  </td>
                  <td>
                    <div className={styles.actions}>
                      <button
                        onClick={() => handleEdit(commercial)}
                        className={styles.btnEdit}
                        title="Modifier"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={() => handleDelete(commercial.id)}
                        className={styles.btnDelete}
                        title="Supprimer"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Commerciaux;
