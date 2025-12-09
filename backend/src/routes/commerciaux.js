const express = require('express');
const router = express.Router();
const db = require('../database');
const { authenticateToken, requireAdmin } = require('../middleware/auth');

// GET /api/commerciaux - Liste tous les commerciaux
router.get('/', authenticateToken, (req, res) => {
  try {
    const commerciaux = db.prepare('SELECT * FROM commerciaux ORDER BY name ASC').all();
    res.json(commerciaux);
  } catch (error) {
    console.error('Erreur lors de la récupération des commerciaux:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

// POST /api/commerciaux - Créer un nouveau commercial (admin uniquement)
router.post('/', authenticateToken, requireAdmin, (req, res) => {
  try {
    const { name, color } = req.body;

    if (!name || !color) {
      return res.status(400).json({ error: 'Le nom et la couleur sont requis' });
    }

    // Valider le format de couleur hex
    const hexColorRegex = /^#[0-9A-F]{6}$/i;
    if (!hexColorRegex.test(color)) {
      return res.status(400).json({ error: 'Format de couleur invalide (utiliser #RRGGBB)' });
    }

    const result = db.prepare('INSERT INTO commerciaux (name, color) VALUES (?, ?)').run(name, color);

    const newCommercial = db.prepare('SELECT * FROM commerciaux WHERE id = ?').get(result.lastInsertRowid);

    res.status(201).json(newCommercial);
  } catch (error) {
    console.error('Erreur lors de la création du commercial:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

// PATCH /api/commerciaux/:id - Modifier un commercial (admin uniquement)
router.patch('/:id', authenticateToken, requireAdmin, (req, res) => {
  try {
    const { id } = req.params;
    const { name, color } = req.body;

    // Vérifier que le commercial existe
    const commercial = db.prepare('SELECT * FROM commerciaux WHERE id = ?').get(id);
    if (!commercial) {
      return res.status(404).json({ error: 'Commercial non trouvé' });
    }

    // Valider le format de couleur si fourni
    if (color) {
      const hexColorRegex = /^#[0-9A-F]{6}$/i;
      if (!hexColorRegex.test(color)) {
        return res.status(400).json({ error: 'Format de couleur invalide (utiliser #RRGGBB)' });
      }
    }

    // Construire la requête de mise à jour
    const updates = [];
    const params = [];

    if (name !== undefined) {
      updates.push('name = ?');
      params.push(name);
    }
    if (color !== undefined) {
      updates.push('color = ?');
      params.push(color);
    }

    if (updates.length === 0) {
      return res.status(400).json({ error: 'Aucune modification fournie' });
    }

    params.push(id);
    db.prepare(`UPDATE commerciaux SET ${updates.join(', ')} WHERE id = ?`).run(...params);

    const updatedCommercial = db.prepare('SELECT * FROM commerciaux WHERE id = ?').get(id);
    res.json(updatedCommercial);
  } catch (error) {
    console.error('Erreur lors de la modification du commercial:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

// DELETE /api/commerciaux/:id - Supprimer un commercial (admin uniquement)
router.delete('/:id', authenticateToken, requireAdmin, (req, res) => {
  try {
    const { id } = req.params;

    // Vérifier que le commercial existe
    const commercial = db.prepare('SELECT * FROM commerciaux WHERE id = ?').get(id);
    if (!commercial) {
      return res.status(404).json({ error: 'Commercial non trouvé' });
    }

    // Vérifier si le commercial est assigné à des rendez-vous
    const assignedCount = db.prepare('SELECT COUNT(*) as count FROM appointments WHERE commercial_id = ?').get(id);
    if (assignedCount.count > 0) {
      return res.status(400).json({
        error: `Impossible de supprimer ce commercial car il est assigné à ${assignedCount.count} rendez-vous. Réassignez ces rendez-vous avant de supprimer.`
      });
    }

    db.prepare('DELETE FROM commerciaux WHERE id = ?').run(id);

    res.json({ message: 'Commercial supprimé avec succès' });
  } catch (error) {
    console.error('Erreur lors de la suppression du commercial:', error);
    res.status(500).json({ error: 'Erreur serveur' });
  }
});

module.exports = router;
