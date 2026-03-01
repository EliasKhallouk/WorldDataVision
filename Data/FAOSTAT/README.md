# FAOSTAT Datasets

Ce dossier contient les datasets de la FAO (Food and Agriculture Organization).

## 📥 Téléchargement

Les fichiers de données bruts (`*_All_Data_*.csv`) ne sont **pas versionnés** car trop volumineux (>100 MB).

Pour obtenir les datasets :

```bash
# Inputs - Land Use (46.7 MB)
wget https://fenixservices.fao.org/faostat/static/bulkdownloads/Inputs_LandUse_E_All_Data_\(Normalized\).zip
unzip Inputs_LandUse_E_All_Data_\(Normalized\).zip

# Production - Crops & Livestock (519.8 MB)
wget https://fenixservices.fao.org/faostat/static/bulkdownloads/Production_Crops_Livestock_E_All_Data_\(Normalized\).zip
unzip Production_Crops_Livestock_E_All_Data_\(Normalized\).zip

# Production - Indices (311.3 MB)
wget https://fenixservices.fao.org/faostat/static/bulkdownloads/Production_Indices_E_All_Data_\(Normalized\).zip
unzip Production_Indices_E_All_Data_\(Normalized\).zip
```

## 📊 Fichiers présents

### Fichiers de métadonnées (versionnés)
- `Inputs_LandUse_E_AreaCodes.csv` - Codes pays
- `Inputs_LandUse_E_Elements.csv` - Codes éléments
- `Inputs_LandUse_E_ItemCodes.csv` - Codes catégories
- `Inputs_LandUse_E_Flags.csv` - Codes drapeaux
- `Production_Indices_E_*.csv` - Métadonnées indices production
- `Production_Crops_Livestock_E_*.csv` - Métadonnées production

### Fichiers de données (non versionnés, à télécharger)
- `Inputs_LandUse_E_All_Data_(Normalized).csv` - 46.7 MB
- `Production_Crops_Livestock_E_All_Data_(Normalized).csv` - 519.8 MB
- `Production_Indices_E_All_Data_(Normalized).csv` - 311.3 MB

## 🔧 Utilisation

Une fois téléchargés, utilisez les scripts d'import :

```bash
python3 scripts/import/import_faostat.py
python3 scripts/import/import_faostat_production.py
```

## 📚 Documentation

- [FAOSTAT Bulk Downloads](https://www.fao.org/faostat/en/#data)
- [Script d'import Land Use](../../scripts/import/import_faostat.py)
- [Script d'import Production](../../scripts/import/import_faostat_production.py)
