# IDB Datasets

Ce dossier contient les datasets de la IDB (Inter-American Development Bank).

## 📥 Note importante

Les fichiers de données CSV ne sont **pas versionnés** car volumineux et redondants avec la base de données.

## 📁 Structure

Chaque indicateur est dans son propre dossier avec 2 fichiers :
- `{indicator_name}.csv` - Données (non versionné)
- `{indicator_name}_metadata.csv` - Métadonnées (non versionné)

## 📊 Indicateurs disponibles

### 👨‍🎓 Éducation
- Attenadance rate 4-5 years old
- Attenadance rate 6-11 years old
- Attenadance rate 12-14 years old
- Attenadance rate 15-17 years old
- Attenadance rate 18-23 years old
- Average years of education of people aged 25+
- Average years of schooling
- Completion rate in primary education
- Completion rate in secondary education
- Completion rate in tertiary education

### 👨‍⚕️ Santé
- Medical doctors per 10 000 population

### 👥 Démographie
- Percentage of migrants in population
- Percentage of population residing in rural areas
- Percentage of population residing in urban areas
- Percentage of unemployed population

## 🔧 Import dans la BDD

Les données sont déjà importées dans PostgreSQL. Pour réimporter :

```bash
python3 scripts/import/import_idb_indicators.py
```

## 🌐 Source

[IDB Numbers Portal](https://numbers.iadb.org/)

## 📈 Statistiques

- **3 indicateurs** mappés vers IRC
- **~3,532 valeurs** importées
- Région: **Amérique latine et Caraïbes**
- Taux de correspondance: **~100%** (région couverte)
