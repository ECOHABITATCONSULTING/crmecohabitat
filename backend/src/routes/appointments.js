const express = require('express');
const db = require('../database');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Récupérer les RDV d'un utilisateur
router.get('/', authenticateToken, (req, res) => {
  try {
    const { date, user_id, commercial_id, filter_mode } = req.query;
    let query = `
      SELECT
        appointments.*,
        COALESCE(leads.first_name, clients.first_name) as first_name,
        COALESCE(leads.last_name, clients.last_name) as last_name,
        COALESCE(leads.postal_code, clients.postal_code) as postal_code,
        users.username,
        commerciaux.name as commercial_name,
        commerciaux.color as commercial_color
      FROM appointments
      LEFT JOIN leads ON appointments.lead_id = leads.id
      LEFT JOIN clients ON appointments.client_id = clients.id
      JOIN users ON appointments.user_id = users.id
      LEFT JOIN commerciaux ON appointments.commercial_id = commerciaux.id
      WHERE 1=1
    `;
    let params = [];

    // PHASE 2.2 - Les agents voient TOUS les RDV (plus de filtre automatique)
    // Mais on garde les filtres manuels ci-dessous

    // Filtrer par date si fournie
    if (date) {
      query += ' AND appointments.date = ?';
      params.push(date);
    }

    // Filtres par user_id et/ou commercial_id
    if (user_id || commercial_id) {
      const mode = filter_mode === 'OR' ? 'OR' : 'AND';

      if (user_id && commercial_id) {
        if (mode === 'AND') {
          query += ' AND appointments.user_id = ? AND appointments.commercial_id = ?';
          params.push(user_id, commercial_id);
        } else {
          query += ' AND (appointments.user_id = ? OR appointments.commercial_id = ?)';
          params.push(user_id, commercial_id);
        }
      } else if (user_id) {
        query += ' AND appointments.user_id = ?';
        params.push(user_id);
      } else if (commercial_id) {
        query += ' AND appointments.commercial_id = ?';
        params.push(commercial_id);
      }
    }

    query += ' ORDER BY date, time';

    const appointments = db.prepare(query).all(...params);
    res.json(appointments);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Récupérer les RDV d'un lead
router.get('/lead/:leadId', authenticateToken, (req, res) => {
  try {
    const { leadId } = req.params;

    const appointments = db.prepare(`
      SELECT appointments.*, users.username
      FROM appointments
      JOIN users ON appointments.user_id = users.id
      WHERE lead_id = ?
      ORDER BY date DESC, time DESC
    `).all(leadId);

    res.json(appointments);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Créer un RDV
router.post('/', authenticateToken, (req, res) => {
  try {
    const { lead_id, client_id, title, date, time, commercial_id } = req.body;

    if ((!lead_id && !client_id) || !title || !date || !time) {
      return res.status(400).json({ error: 'Données manquantes' });
    }

    // Un agent ne peut créer des RDV que pour lui-même
    const user_id = req.user.role === 'admin' && req.body.user_id ? req.body.user_id : req.user.id;

    const result = db.prepare('INSERT INTO appointments (lead_id, client_id, user_id, title, date, time, commercial_id) VALUES (?, ?, ?, ?, ?, ?, ?)').run(
      lead_id || null,
      client_id || null,
      user_id,
      title,
      date,
      time,
      commercial_id || null
    );

    const appointment = db.prepare(`
      SELECT
        appointments.*,
        COALESCE(leads.first_name, clients.first_name) as first_name,
        COALESCE(leads.last_name, clients.last_name) as last_name,
        COALESCE(leads.postal_code, clients.postal_code) as postal_code,
        users.username,
        commerciaux.name as commercial_name,
        commerciaux.color as commercial_color
      FROM appointments
      LEFT JOIN leads ON appointments.lead_id = leads.id
      LEFT JOIN clients ON appointments.client_id = clients.id
      JOIN users ON appointments.user_id = users.id
      LEFT JOIN commerciaux ON appointments.commercial_id = commerciaux.id
      WHERE appointments.id = ?
    `).get(result.lastInsertRowid);

    res.status(201).json(appointment);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Mettre à jour un RDV
router.patch('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const { title, date, time, commercial_id } = req.body;

    // PHASE 2.3 - Vérifier les permissions pour les agents
    if (req.user.role === 'agent') {
      const appointment = db.prepare('SELECT user_id FROM appointments WHERE id = ?').get(id);
      if (!appointment) {
        return res.status(404).json({ error: 'Rendez-vous introuvable' });
      }
      if (appointment.user_id !== req.user.id) {
        return res.status(403).json({ error: 'Vous ne pouvez modifier que vos propres rendez-vous' });
      }
    }

    const updates = [];
    const params = [];

    if (title !== undefined) { updates.push('title = ?'); params.push(title); }
    if (date !== undefined) { updates.push('date = ?'); params.push(date); }
    if (time !== undefined) { updates.push('time = ?'); params.push(time); }
    if (commercial_id !== undefined) { updates.push('commercial_id = ?'); params.push(commercial_id || null); }

    if (updates.length === 0) {
      return res.status(400).json({ error: 'Aucune donnée à mettre à jour' });
    }

    params.push(id);
    db.prepare(`UPDATE appointments SET ${updates.join(', ')} WHERE id = ?`).run(...params);

    const appointment = db.prepare(`
      SELECT
        appointments.*,
        COALESCE(leads.first_name, clients.first_name) as first_name,
        COALESCE(leads.last_name, clients.last_name) as last_name,
        COALESCE(leads.postal_code, clients.postal_code) as postal_code,
        users.username,
        commerciaux.name as commercial_name,
        commerciaux.color as commercial_color
      FROM appointments
      LEFT JOIN leads ON appointments.lead_id = leads.id
      LEFT JOIN clients ON appointments.client_id = clients.id
      JOIN users ON appointments.user_id = users.id
      LEFT JOIN commerciaux ON appointments.commercial_id = commerciaux.id
      WHERE appointments.id = ?
    `).get(id);

    res.json(appointment);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Supprimer un RDV
router.delete('/:id', authenticateToken, (req, res) => {
  try {
    const { id } = req.params;
    const appointment = db.prepare('SELECT * FROM appointments WHERE id = ?').get(id);

    if (!appointment) {
      return res.status(404).json({ error: 'RDV introuvable' });
    }

    // Seul l'utilisateur concerné ou un admin peut supprimer
    if (appointment.user_id !== req.user.id && req.user.role !== 'admin') {
      return res.status(403).json({ error: 'Non autorisé' });
    }

    db.prepare('DELETE FROM appointments WHERE id = ?').run(id);
    res.json({ message: 'RDV supprimé' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
