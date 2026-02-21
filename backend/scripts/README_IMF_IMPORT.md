# Import des données IMF - Dette Publique

## 📋 Description

Ce script importe les données de dette publique du FMI (Central Government Debt) dans la base de données WorldDataVision pour compléter l'indicateur `GC.DOD.TOTL.GD.ZS`.

## 📁 Fichiers

- **Script d'import** : `backend/scripts/import_imf_debt_data.js`
- **Script de test** : `backend/scripts/test_country_mapping.js`
- **Données source** : `Data/IRC/imf-dm-export-20260221.csv`

## 🚀 Utilisation

### 1. Tester le mapping des pays (recommandé avant l'import)

```bash
cd backend
node scripts/test_country_mapping.js
```

Ce script affiche les 10 premiers pays du fichier IMF et vérifie s'ils sont trouvés dans la base de données.

### 2. Exécuter l'import

```bash
cd backend
node scripts/import_imf_debt_data.js
```

## ⚙️ Fonctionnalités

### Fusion intelligente des données

- **Si une valeur existe déjà** (World Bank) : Calcul de la moyenne `(valeur_wb + valeur_imf) / 2`
- **Si nouvelle valeur** : Insertion directe

### Mapping des pays

Le script utilise plusieurs stratégies :

1. **Mapping manuel** pour les cas spéciaux (ex: "Bahamas, The" → BHS)
2. **Recherche normalisée** (insensible aux accents et à la casse)
3. **Recherche partielle** pour trouver des correspondances approximatives

### Mise à jour des sources

La source de l'indicateur est automatiquement mise à jour vers :
```
"World Bank + IMF (Central Government Debt)"
```

## 📊 Statistiques attendues

Le script affiche à la fin :

- ✅ Nombre de nouvelles valeurs insérées
- 🔄 Nombre de valeurs mises à jour (moyennées)
- ⏭️ Nombre de valeurs ignorées (pays non trouvé)

## ⚠️ Cas spéciaux traités

Pays avec noms différents entre IMF et la base :

- "Bahamas, The" → Bahamas
- "Congo, Dem. Rep." → République démocratique du Congo
- "Congo, Rep." → République du Congo
- "Egypt, Arab Rep." → Égypte
- "Gambia, The" → Gambie
- "Iran, Islamic Rep." → Iran
- "Korea, Rep." → Corée du Sud
- "Kyrgyz Republic" → Kirghizistan
- "Lao PDR" → Laos
- "Russian Federation" → Russie
- "Slovak Republic" → Slovaquie
- "Syrian Arab Republic" → Syrie
- "Türkiye" → Turquie
- "Venezuela, RB" → Venezuela
- "Yemen, Rep." → Yémen

## 🔧 Dépannage

### Erreur "Pays non trouvé"

Si des pays ne sont pas trouvés, ajouter un mapping manuel dans le dictionnaire `COUNTRY_NAME_MAPPING` du script.

### Erreur de connexion PostgreSQL

Vérifier les variables d'environnement :
```bash
DB_USER=elias
DB_NAME=worlddatavision
DB_HOST=localhost
DB_PORT=5432
```

### Transaction rollback

Le script utilise une transaction SQL. En cas d'erreur, toutes les modifications sont annulées automatiquement.

## 📈 Impact attendu

L'import des données IMF devrait :

1. **Augmenter la couverture temporelle** (1950-2024 vs généralement 1990+ pour World Bank)
2. **Améliorer la complétude de l'indicateur** GC.DOD.TOTL.GD.ZS
3. **Permettre le calcul de l'IRC pour plus de pays** (surtout pour les années récentes)

## 🔍 Vérification post-import

Après l'import, vérifier la couverture :

```sql
SELECT 
    COUNT(DISTINCT country_id) as nb_pays,
    MIN(year) as premiere_annee,
    MAX(year) as derniere_annee,
    COUNT(*) as nb_valeurs
FROM indicator_value
WHERE indicator_id = (SELECT id FROM indicator WHERE code = 'GC.DOD.TOTL.GD.ZS');
```

## 📝 Notes

- Le script est **idempotent** : on peut le relancer sans créer de doublons
- La fusion par moyenne est conservatrice et évite les biais
- Les données "no data" du fichier IMF sont automatiquement ignorées
- Les virgules décimales sont converties en points pour PostgreSQL
