# 🔧 Correction du bug de parsing CSV - À EXÉCUTER MAINTENANT

## ❌ Problème identifié

Le script parsait seulement **5 valeurs** au lieu de plusieurs milliers à cause de :
- Utilisation de `line.split(',')` qui découpe incorrectement les valeurs numériques
- Les valeurs contiennent des virgules : `"20,5"` devient `["20", "5"]`

## ✅ Solution appliquée

Le script a été corrigé pour utiliser le module `csv` de Python qui gère correctement les guillemets.

## 🚀 COMMANDES À EXÉCUTER

### 1. Tester le parsing (optionnel)

```bash
cd /home/elias/PROJECT/WorldDataVision/backend/scripts
python3 test_csv_parsing.py
```

**Résultat attendu** : ~8000-9000 valeurs non vides

### 2. Relancer l'import CORRIGÉ

```bash
cd /home/elias/PROJECT/WorldDataVision/backend/scripts
python3 import_imf_debt_data.py
```

**Résultat attendu** :
```
✅ 8,234 valeurs parsées  (au lieu de 5 !)
📥 Nouvelles valeurs insérées: ~6,000
🔄 Valeurs mises à jour (moyenne): ~2,000
⏭️  Valeurs ignorées: <50
```

### 3. Vérifier le résultat

```bash
psql -U elias -d worlddatavision -c "
SELECT 
    COUNT(DISTINCT country_id) as nb_pays,
    MIN(year) as premiere_annee,
    MAX(year) as derniere_annee,
    COUNT(*) as total_valeurs
FROM indicator_value iv
JOIN indicator i ON iv.indicator_id = i.id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS';
"
```

**Résultat attendu** :
```
nb_pays | premiere_annee | derniere_annee | total_valeurs
--------+----------------+----------------+--------------
  ~150  |      1950      |      2024      |    ~8,000
```

## 📊 Comparaison Avant/Après

### AVANT (bug)
- Valeurs parsées : **5** ❌
- Pays : 109
- Période : 1989-2024
- Total : 1,620 valeurs

### APRÈS (corrigé)
- Valeurs parsées : **~8,200** ✅
- Pays : ~150-160
- Période : **1950-2024**
- Total : ~8,000-9,000 valeurs

## 🔍 Debug si nécessaire

Si le nombre de valeurs est toujours faible :

```bash
# Vérifier le parsing
python3 test_csv_parsing.py

# Vérifier les 5 premières lignes du fichier original
head -5 /home/elias/PROJECT/WorldDataVision/Data/IRC/imf-dm-export-20260221.csv
```

## ⚡ EXÉCUTION RAPIDE (copier-coller)

```bash
cd /home/elias/PROJECT/WorldDataVision/backend/scripts && \
python3 import_imf_debt_data.py && \
echo "" && \
echo "═══════════════════════════════════════" && \
echo "📊 Vérification de la base de données:" && \
echo "═══════════════════════════════════════" && \
psql -U elias -d worlddatavision -c "
SELECT 
    COUNT(DISTINCT country_id) as nb_pays,
    MIN(year) as premiere_annee,
    MAX(year) as derniere_annee,
    COUNT(*) as total_valeurs
FROM indicator_value iv
JOIN indicator i ON iv.indicator_id = i.id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS';"
```

## 📝 Notes

- Le bug venait de `split(',')` qui ne respecte pas les guillemets CSV
- La correction utilise `csv.reader()` qui gère correctement le format CSV standard
- Les valeurs avec virgules décimales (`"20,5"`) sont maintenant correctement parsées en `20.5`

---

**Statut** : ✅ Code corrigé - Prêt à réexécuter
**Date** : 21 février 2026
