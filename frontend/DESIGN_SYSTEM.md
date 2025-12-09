# Système de Design - CRM Eco Habitat Consulting

Documentation des standards visuels et des composants CSS.

---

## 🎨 Palette de Couleurs

### Couleurs Principales
```css
--accent-primary: #10b981 (Vert émeraude - Action principale)
--accent-secondary: #059669 (Vert foncé - Hover)
--accent-gradient: linear-gradient(135deg, #059669 0%, #10b981 100%)
```

### Couleurs de Fond
```css
--bg-primary: #ffffff (Fond principal)
--bg-secondary: #f9fafb (Fond sections)
--bg-tertiary: #f3f4f6 (Fond inputs)
```

### Couleurs de Texte
```css
--text-primary: #111827 (Texte principal - noir)
--text-secondary: #6b7280 (Texte secondaire - gris)
```

### Couleurs Sémantiques
```css
--success: #10b981 (Vert - Succès)
--warning: #f59e0b (Ambre - Attention)
--danger: #ef4444 (Rouge - Erreur/Suppression)
--info: #3b82f6 (Bleu - Information)
```

### Bordures
```css
--border-color: #e5e7eb (Bordure standard)
```

---

## 📏 Espacement

### Échelle de Spacing
- **Small**: 8px, 12px
- **Medium**: 16px, 20px, 24px
- **Large**: 32px, 40px, 48px

### Padding Standard
- **Conteneurs**: 20-32px
- **Cartes**: 16-24px
- **Boutons**: Voir section Boutons

---

## 🔘 Boutons

### Tailles de Boutons
```css
/* Small */
padding: 0.5rem 1rem;      /* 8px 16px */
font-size: 0.875rem;       /* 14px */

/* Medium (Standard) */
padding: 0.75rem 1.5rem;   /* 12px 24px */
font-size: 0.875rem;       /* 14px */

/* Large */
padding: 1rem 2rem;        /* 16px 32px */
font-size: 1rem;           /* 16px */
```

### Variantes de Boutons

#### Primary (Action principale)
```css
background: linear-gradient(135deg, #059669 0%, #10b981 100%);
color: white;
border: none;
border-radius: 8px;
font-weight: 600;
transition: transform 0.2s, box-shadow 0.2s;

:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}
```

#### Secondary (Action secondaire)
```css
background: var(--bg-tertiary);
color: var(--text-primary);
border: 1px solid var(--border-color);
border-radius: 8px;
font-weight: 500;

:hover {
  background: var(--bg-secondary);
}
```

#### Danger (Suppression)
```css
background: rgba(239, 68, 68, 0.2);
color: #ef4444;
border: 1px solid rgba(239, 68, 68, 0.3);
border-radius: 8px;

:hover {
  background: rgba(239, 68, 68, 0.3);
}
```

#### Ghost (Transparent)
```css
background: transparent;
color: var(--text-secondary);
border: 1px solid var(--border-color);
border-radius: 8px;

:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}
```

### Border Radius Standards
- **Petits éléments** (badges, tags): 6px
- **Boutons, inputs**: 8px
- **Cartes, modals**: 12-16px

---

## 📝 Formulaires

### Input Fields
```css
.input {
  padding: 0.75rem;              /* 12px */
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.input:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}
```

### Labels
```css
.label {
  font-size: 0.875rem;     /* 14px */
  font-weight: 500-600;
  color: var(--text-primary);
  margin-bottom: 0.5rem;   /* 8px */
}
```

### Select Dropdowns
```css
.select {
  /* Même style que .input */
  background: var(--bg-tertiary);
  padding: 0.75rem;
  border-radius: 8px;
}
```

---

## 🪟 Modals

### Structure Modal
```css
/* Overlay */
.overlay {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
}

/* Modal Container */
.modal {
  background: var(--bg-secondary);
  border-radius: 16px;
  max-width: 700px;            /* Standard */
  max-height: 90vh;
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.15);
}
```

### Tailles de Modal
- **Small**: 500px
- **Medium**: 700px (Standard)
- **Large**: 900px
- **XLarge**: 1200px

---

## 📊 Tables

### Header
```css
.table thead {
  background: rgba(16, 185, 129, 0.05);  /* Teinte verte subtile */
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}
```

### Rows
```css
.table tbody tr {
  transition: background-color 0.2s;
}

.table tbody tr:hover {
  background: rgba(16, 185, 129, 0.04);  /* Hover vert léger */
}

.table td {
  padding: 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}
```

---

## 🎭 Status Badges

### Status Colors
```javascript
const statusColors = {
  nouveau: '#3b82f6',      // Bleu
  contacte: '#8b5cf6',     // Violet
  rdv_pris: '#f59e0b',     // Orange
  devis_envoye: '#10b981', // Vert
  gagne: '#059669',        // Vert foncé
  perdu: '#ef4444'         // Rouge
};
```

### Badge Style
```css
.badge {
  padding: 0.25rem 0.75rem;  /* 4px 12px */
  border-radius: 6px;
  font-size: 0.75rem;        /* 12px */
  font-weight: 600;
  text-transform: capitalize;
}
```

---

## 📱 Responsive Breakpoints

```css
/* Tablette */
@media (max-width: 1200px) {
  /* Grid 2 colonnes → 1 colonne */
}

/* Mobile */
@media (max-width: 768px) {
  /* Menu latéral → Hamburger */
  /* Padding réduit: 1rem */
  /* Font sizes -10% */
}

/* Petit mobile */
@media (max-width: 480px) {
  /* Tables scrollables horizontalement */
  /* Modals plein écran */
}
```

---

## ✨ Animations

### Transitions Standard
```css
transition: all 0.2s ease;
```

### Hover Effects
```css
:hover {
  transform: translateY(-1px) à translateY(-2px);
  box-shadow: enhanced shadow;
}
```

### Animation Fade In
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## 🎯 Typography

### Font Family
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Hiérarchie
```css
/* Page Title */
font-size: 2rem;         /* 32px */
font-weight: 700;

/* Section Title */
font-size: 1.5rem;       /* 24px */
font-weight: 600;

/* Subsection Title */
font-size: 1.25rem;      /* 20px */
font-weight: 600;

/* Body Text */
font-size: 0.875rem;     /* 14px */
font-weight: 400;

/* Small Text */
font-size: 0.75rem;      /* 12px */
font-weight: 400;
```

### Letter Spacing
- **Headers uppercase**: 0.05em
- **Body text**: normal
- **Buttons**: 0.01em

---

## 🛡️ Ombres (Shadows)

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

### Utilisation
- **Cards**: shadow-sm
- **Modals**: shadow-lg
- **Hover buttons**: shadow-md

---

## ⚡ Bonnes Pratiques

### ✅ À FAIRE
1. Utiliser les variables CSS (`var(--accent-primary)`)
2. Respecter l'échelle d'espacement (8, 12, 16, 20, 24, 32px)
3. Utiliser `rem` pour les tailles de police
4. Border-radius cohérent (6-8-12-16px)
5. Transitions sur tous les états interactifs
6. Tester responsive (mobile, tablette, desktop)

### ❌ À ÉVITER
1. Hardcoder des couleurs hex au lieu d'utiliser les variables
2. Mélanger px/rem/em de manière incohérente
3. Créer des border-radius arbitraires (ex: 13px, 19px)
4. Oublier les états :hover et :focus
5. Utiliser des animations trop longues (> 0.3s)
6. Négliger l'accessibilité (contraste, focus visible)

---

## 🎨 Palette Commerciaux

Les commerciaux peuvent choisir des couleurs personnalisées pour leurs rendez-vous.

### Couleurs Suggérées
```css
#3b82f6  /* Bleu */
#8b5cf6  /* Violet */
#f59e0b  /* Orange */
#10b981  /* Vert */
#ef4444  /* Rouge */
#06b6d4  /* Cyan */
#f43f5e  /* Rose */
```

---

## 📦 CSS Modules

### Naming Convention
```javascript
// PascalCase pour les composants
ComponentName.jsx
ComponentName.module.css

// camelCase pour les classes CSS
.submitBtn
.formGroup
.tableContainer
```

---

## 🔍 Accessibilité

### Contrastes Minimum
- **Texte normal**: 4.5:1
- **Texte large**: 3:1
- **Éléments UI**: 3:1

### Focus Visible
```css
:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}
```

### Labels
- Toujours associer `<label>` avec `<input>`
- Utiliser `aria-label` si pas de label visible

---

**Version**: 1.0
**Dernière mise à jour**: 2025-12-09
**Auteur**: Système CRM Eco Habitat Consulting
