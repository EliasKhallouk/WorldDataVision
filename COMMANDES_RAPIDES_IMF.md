# 🎯 Import IMF - Commandes rapides

## ⚡ Quick Start (3 étapes)

### 1️⃣ Vérifier les prérequis

```bash
cd /home/elias/PROJECT/WorldDataVision/backend/scripts
python3 check_import_prerequisites.py
```

**Attendu** : Tous les checks ✅

### 2️⃣ Lancer l'import

```bash
python3 import_imf_debt_data.py
```

**Durée estimée** : ~30-60 secondes

### 3️⃣ Vérifier le résultat

```bash
psql -U elias -d worlddatavision -c "
SELECT 
    COUNT(DISTINCT country_id) as pays,
    MIN(year) as premiere_annee,
    MAX(year) as derniere_annee,
    COUNT(*) as nb_valeurs
FROM indicator_value iv
JOIN indicator i ON iv.indicator_id = i.id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS';
"
```

**Attendu** : 
- Pays : ~150+
- Première année : 1950 ou antérieure
- Dernière année : 2024
- Nb valeurs : ~8,000+

---

## 📋 Commandes de diagnostic

### Vérifier l'indicateur avant import

```sql
SELECT 
    i.code,
    i.name,
    i.source,
    COUNT(DISTINCT iv.country_id) as nb_pays,
    MIN(iv.year) as annee_debut,
    MAX(iv.year) as annee_fin,
    COUNT(*) as nb_valeurs
FROM indicator i
LEFT JOIN indicator_value iv ON i.id = iv.indicator_id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS'
GROUP BY i.id, i.code, i.name, i.source;
```

### Top 10 des pays avec le plus de données

```sql
SELECT 
    c.name as pays,
    c.iso3,
    COUNT(*) as nb_annees,
    MIN(iv.year) as premiere_annee,
    MAX(iv.year) as derniere_annee,
    ROUND(AVG(iv.value)::numeric, 2) as dette_moy_pct
FROM indicator_value iv
JOIN country c ON iv.country_id = c.id
JOIN indicator i ON iv.indicator_id = i.id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS'
GROUP BY c.id, c.name, c.iso3
ORDER BY nb_annees DESC
LIMIT 10;
```

### Pays avec données pour 2023

```sql
SELECT 
    c.name,
    c.iso3,
    iv.value as dette_2023_pct
FROM indicator_value iv
JOIN country c ON iv.country_id = c.id
JOIN indicator i ON iv.indicator_id = i.id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS'
    AND iv.year = 2023
ORDER BY iv.value DESC;
```

### Évolution temporelle de la couverture

```sql
SELECT 
    iv.year,
    COUNT(DISTINCT iv.country_id) as nb_pays,
    ROUND(AVG(iv.value)::numeric, 2) as dette_moy_mondiale
FROM indicator_value iv
JOIN indicator i ON iv.indicator_id = i.id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS'
    AND iv.year >= 1990
GROUP BY iv.year
ORDER BY iv.year;
```

---

## 🔧 Dépannage

### Installer psycopg2 si manquant

```bash
pip install psycopg2-binary
# OU
pip3 install psycopg2-binary
```

### Relancer l'import après une erreur

Le script est **idempotent**. Tu peux le relancer sans problème :

```bash
python3 import_imf_debt_data.py
```

Les transactions SQL garantissent qu'en cas d'erreur, rien n'est committé.

### Voir les logs d'un import précédent

```bash
ls -lth /tmp/imf_import_*.log
cat /tmp/imf_import_20260221_*.log
```

### Rollback manuel si nécessaire

Si tu veux annuler un import (ATTENTION : utiliser avec précaution) :

```sql
-- NE PAS EXÉCUTER À MOINS D'ÊTRE SÛR
-- Ceci supprime TOUTES les valeurs de l'indicateur
DELETE FROM indicator_value
WHERE indicator_id = (SELECT id FROM indicator WHERE code = 'GC.DOD.TOTL.GD.ZS');

-- Remettre la source d'origine
UPDATE indicator 
SET source = 'World Bank'
WHERE code = 'GC.DOD.TOTL.GD.ZS';
```

---

## 📊 Analyser l'impact sur l'IRC

### Relancer le diagnostic de complétude

```bash
cd /home/elias/PROJECT/WorldDataVision
jupyter notebook notebooks/diagnostic_irc_completeness.ipynb
```

### Comparer avant/après

**Avant import** :
- Section 7 : GC.DOD.TOTL.GD.ZS dans le top 10 des bottlenecks
- Section 6 : Pilier 2 (Économie) avec faible couverture

**Après import** :
- Section 7 : GC.DOD.TOTL.GD.ZS hors du top 10 ✅
- Section 6 : Pilier 2 avec meilleure couverture 📈
- Section 11 : Plus de pays avec ≥5 pillars 🎯

### Recalculer l'IRC

Une fois les données importées, relancer le calcul IRC complet :

```sql
-- Script de calcul IRC à créer/exécuter
-- (dépend de ton implémentation actuelle)
```

---

## 📈 Statistiques attendues

### Avant l'import

```
Indicateur: GC.DOD.TOTL.GD.ZS
- Pays: ~100-120
- Période: 1990-2022
- Valeurs: ~3,000-4,000
- Source: "World Bank"
```

### Après l'import

```
Indicateur: GC.DOD.TOTL.GD.ZS
- Pays: ~150-170
- Période: 1950-2024
- Valeurs: ~8,000-10,000
- Source: "World Bank + IMF (Central Government Debt)"
```

### Amélioration attendue

- ➕ **50-70 pays supplémentaires**
- ➕ **40 années supplémentaires** (1950-1990)
- ➕ **5,000-6,000 valeurs** de plus
- ✅ **Meilleure couverture IRC** pour les années récentes

---

## 📝 Fichiers créés

```
backend/scripts/
├── import_imf_debt_data.js              # Version Node.js
├── import_imf_debt_data.py              # Version Python ⭐
├── check_import_prerequisites.py        # Vérification pré-import
├── test_country_mapping.js              # Test mapping pays
├── run_imf_import.sh                    # Wrapper shell
└── README_IMF_IMPORT.md                 # Documentation complète

Documentation/
├── GUIDE_IMPORT_IMF.md                  # Guide complet
└── COMMANDES_RAPIDES_IMF.md             # Ce fichier
```

---

## 🎯 Checklist complète

- [ ] Vérifier prérequis : `python3 check_import_prerequisites.py`
- [ ] Lancer import : `python3 import_imf_debt_data.py`
- [ ] Vérifier stats : requête SQL ci-dessus
- [ ] Relancer diagnostic IRC : notebook
- [ ] Vérifier carte mondiale : frontend
- [ ] Recalculer IRC si nécessaire

---

**Date** : 21 février 2026  
**Auteur** : GitHub Copilot  
**Source** : FMI - Central Government Debt (Percent of GDP)
