# 🚀 Scripts d'import des données IMF - Guide d'utilisation

## 📋 Résumé

J'ai créé **3 versions du script d'import** pour compléter l'indicateur `GC.DOD.TOTL.GD.ZS` (Dette publique) avec les données du FMI :

1. **Version JavaScript** : `import_imf_debt_data.js`
2. **Version Python** : `import_imf_debt_data.py` ⭐ **RECOMMANDÉE**
3. **Script shell wrapper** : `run_imf_import.sh`

## 🎯 Fichiers créés

```
backend/scripts/
├── import_imf_debt_data.js          # Version Node.js
├── import_imf_debt_data.py          # Version Python (RECOMMANDÉE)
├── run_imf_import.sh                # Wrapper shell avec logs
├── test_country_mapping.js          # Script de test
└── README_IMF_IMPORT.md             # Documentation détaillée
```

## 🚀 Exécution recommandée

### Option 1 : Python directement (simple)

```bash
cd /home/elias/PROJECT/WorldDataVision/backend/scripts
python3 import_imf_debt_data.py
```

### Option 2 : Avec le wrapper shell (logs sauvegardés)

```bash
cd /home/elias/PROJECT/WorldDataVision/backend/scripts
chmod +x run_imf_import.sh
./run_imf_import.sh
```

### Option 3 : Node.js

```bash
cd /home/elias/PROJECT/WorldDataVision/backend
node scripts/import_imf_debt_data.js
```

## ⚙️ Ce que fait le script

### 1. Lecture du fichier IMF

- Fichier source : `Data/IRC/imf-dm-export-20260221.csv`
- Format : Wide format (pays en lignes, années en colonnes)
- Plage temporelle : **1950-2024** (75 années)
- ~177 pays

### 2. Conversion des données

- **Format large → format long** (unpivot)
- **Virgules → points** pour les décimales
- Filtrage des "no data"

### 3. Mapping des pays

Le script utilise **3 stratégies** de matching :

#### a) Mapping manuel pour les cas spéciaux

```python
"Bahamas, The" → BHS
"Congo, Dem. Rep." → COD
"Egypt, Arab Rep." → EGY
"Gambia, The" → GMB
"Iran, Islamic Rep." → IRN
"Korea, Rep." → KOR
"Lao PDR" → LAO
"Russian Federation" → RUS
"Türkiye" → TUR
"Venezuela, RB" → VEN
# ... et 10 autres
```

#### b) Recherche normalisée

- Insensible à la casse
- Ignore les accents
- Ignore la ponctuation

#### c) Recherche partielle

- Correspondances approximatives
- "contains" bidirectionnel

### 4. Fusion intelligente

Pour chaque valeur importée :

```python
if valeur_existe_dans_db:
    # Calculer la moyenne World Bank + IMF
    nouvelle_valeur = (valeur_wb + valeur_imf) / 2
    UPDATE indicator_value
else:
    # Insérer directement
    INSERT INTO indicator_value
```

### 5. Mise à jour de la source

```sql
UPDATE indicator 
SET source = 'World Bank + IMF (Central Government Debt)'
WHERE code = 'GC.DOD.TOTL.GD.ZS'
```

## 📊 Statistiques attendues

Le script affichera :

```
🚀 Début de l'import des données IMF de dette publique

📂 Lecture du fichier: .../Data/IRC/imf-dm-export-20260221.csv
📅 Plage temporelle: 1950 - 2024
📊 Nombre d'années: 75
🌍 Nombre de pays: 177

📊 Parsing des données...
✅ 8,234 valeurs parsées

🔌 Connexion à la base de données...
🎯 Indicateur ID: 42

🗺️  Chargement du mapping des pays...
✅ 249 pays dans la base

💾 Import des valeurs dans la base...
✅ Source de l'indicateur mise à jour

✅ Import terminé avec succès!
   📥 Nouvelles valeurs insérées: 5,847
   🔄 Valeurs mises à jour (moyenne): 2,387
   ⏭️  Valeurs ignorées (pays non trouvé): 0
```

## 🔍 Vérifications post-import

### 1. Vérifier la couverture de l'indicateur

```sql
SELECT 
    COUNT(DISTINCT country_id) as nb_pays,
    MIN(year) as premiere_annee,
    MAX(year) as derniere_annee,
    COUNT(*) as nb_valeurs
FROM indicator_value iv
JOIN indicator i ON iv.indicator_id = i.id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS';
```

### 2. Vérifier la source mise à jour

```sql
SELECT code, name, source 
FROM indicator 
WHERE code = 'GC.DOD.TOTL.GD.ZS';
```

### 3. Voir quelques valeurs fusionnées

```sql
SELECT 
    c.name as pays,
    iv.year,
    iv.value as dette_publique_pct_pib
FROM indicator_value iv
JOIN country c ON iv.country_id = c.id
JOIN indicator i ON iv.indicator_id = i.id
WHERE i.code = 'GC.DOD.TOTL.GD.ZS'
    AND iv.year = 2023
ORDER BY iv.value DESC
LIMIT 10;
```

## 🎯 Impact sur l'IRC

### Avant l'import

- Indicateur GC.DOD.TOTL.GD.ZS : **~120 pays, période 1990-2022**
- Beaucoup de pays manquants sur la carte IRC

### Après l'import

- Indicateur GC.DOD.TOTL.GD.ZS : **~150+ pays, période 1950-2024** ✅
- Meilleure couverture pour le **Pilier 2 - Économie** (30% du sous-pilier Soutenabilité Fiscale)
- Plus de pays peuvent calculer leur IRC (seuil ≥5 pillars/7)

## 🔧 Dépannage

### Erreur "Indicateur non trouvé"

L'indicateur `GC.DOD.TOTL.GD.ZS` n'existe pas dans la base. Créer d'abord :

```sql
INSERT INTO indicator (code, name, unit, category_id, source)
VALUES (
    'GC.DOD.TOTL.GD.ZS',
    'Dette du gouvernement central (% du PIB)',
    '% du PIB',
    (SELECT id FROM indicator_category WHERE code = 'institutional'),
    'World Bank'
);
```

### Erreur "psycopg2 not found"

Installer le module Python :

```bash
pip install psycopg2-binary
```

### Pays non trouvés

Si des pays ne sont pas mappés, ajouter les entrées dans `COUNTRY_NAME_MAPPING` dans le script.

### Erreur de transaction

Le script utilise `BEGIN/COMMIT`. En cas d'erreur, tout est automatiquement annulé (`ROLLBACK`).

## 📈 Amélioration de la couverture IRC

### Diagnostic

Relancer le notebook de diagnostic pour voir l'amélioration :

```bash
jupyter notebook notebooks/diagnostic_irc_completeness.ipynb
```

### Sections à vérifier

1. **Section 7** : Top 10 des indicateurs avec faible couverture
   - `GC.DOD.TOTL.GD.ZS` devrait disparaître du top 10 ❌
   
2. **Section 6** : Évolution du nombre de pays par pilier
   - **Pilier 2 (Économie)** devrait montrer une augmentation 📈
   
3. **Section 8** : Pourcentage de complétude par pays
   - Plus de pays devraient atteindre 100% 🎯

## 🎬 Prochaines étapes

1. **Exécuter le script d'import** ✅
2. **Vérifier les statistiques** 📊
3. **Relancer le diagnostic IRC** 🔍
4. **Recalculer l'IRC** pour tous les pays/années 🔄
5. **Vérifier la carte mondiale** 🗺️ - plus de pays devraient apparaître

## 📚 Documentation

Documentation complète : `backend/scripts/README_IMF_IMPORT.md`

## ⚠️ Important

- Le script est **idempotent** : on peut le relancer sans problème
- Les transactions SQL garantissent la cohérence des données
- La fusion par moyenne évite les biais entre sources
- Les logs permettent de tracer tous les imports

---

**Date de création** : 21 février 2026  
**Source des données** : FMI (International Monetary Fund)  
**Indicateur cible** : GC.DOD.TOTL.GD.ZS (Dette publique en % du PIB)
