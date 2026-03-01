# Scripts d'Import de Données

Ce dossier contient tous les scripts Python utilisés pour importer et enrichir les données dans la base PostgreSQL `worlddatavision`.

## 📋 Scripts disponibles

### 🌐 ITU (International Telecommunication Union)

- **`import_mobile_subscriptions_complete.py`**
  - Indicateur: `IT.CEL.SETS.P2` (Abonnements mobiles pour 100 habitants)
  - Sources: World Bank + ITU
  - Résultat: 10,729 valeurs, 222 pays
  - Stratégie: Moyenne en cas de conflit

- **`import_broadband_itu.py`**
  - Indicateur: `IT.NET.BBND.P2` (Abonnements haut débit fixe pour 100 habitants)
  - Sources: World Bank + ITU
  - Résultat: 4,337 valeurs, 212 pays
  - Stratégie: Moyenne en cas de conflit

### 🌾 FAOSTAT (Food and Agriculture Organization)

- **`import_faostat.py`**
  - Indicateurs: `AG.LND.AGRI.ZS`, `AG.LND.TOTL.K2`
  - Source: FAOSTAT Inputs_LandUse dataset
  - Résultat: 18,611 valeurs
  - Conversion: 1000 ha → km² (factor 0.01)

- **`import_faostat_production.py`**
  - Indicateurs: `AG.PRD.FOOD.XD`, `AG.PRD.CROP.XD`, `AG.PRD.LVSK.XD`
  - Source: FAOSTAT Production_Indices dataset
  - Résultat: 25,677 valeurs (indices de production)

### 🏦 IDB (Inter-American Development Bank)

- **`import_idb_indicators.py`**
  - Indicateurs: Chômage, densité médicale, urbanisation
  - Source: IDB datasets
  - Résultat: 3,532 opérations, 3 indicateurs enrichis

### 🎓 AfDB (African Development Bank)

- **`import_ifdb_literacy.py`**
  - Indicateur: `SE.ADT.LITR.ZS` (Taux d'alphabétisation)
  - Source: AfDB IfDB dataset
  - Résultat: ~257 valeurs enrichies

## ⚙️ Stratégie d'Import

**Tous les scripts utilisent la stratégie d'AVERAGING** pour les conflits de données :

```python
ON CONFLICT (indicator_id, country_id, year) 
DO UPDATE SET value = (EXCLUDED.value + indicator_value.value) / 2
```

Cette stratégie garantit qu'aucune donnée n'est perdue et que la moyenne entre sources multiples est calculée.

## 🗂️ Mapping Pays

Les scripts incluent des dictionnaires de mapping pour convertir les noms de pays :
- **Anglais → Français** : COUNTRY_MAPPING (624+ variantes)
- **FAOSTAT → BDD** : COUNTRY_MAPPING_FAO (596+ variantes)
- **IDB codes** : Mapping spécifique IDB

## 📊 Taux de Correspondance

- **ITU** : ~70-80% (161-222 pays selon indicateur)
- **FAOSTAT** : ~60-70% (161-165 pays matchés)
- **IDB** : ~100% (région Amérique latine/Caraïbes)
- **AfDB** : ~40-50% (région Afrique)

## 🔄 Ordre d'Exécution Recommandé

1. Importer World Bank (déjà dans IRC/)
2. Enrichir avec sources externes dans cet ordre :
   - AfDB (literacy)
   - IDB (3 indicateurs)
   - ITU (mobile, broadband)
   - FAOSTAT (land use, production)

## 📝 Notes Importantes

- **Déduplication** : Les scripts FAOSTAT utilisent `values_dict` pour dédupliquer les données avant INSERT
- **Conversion d'unités** : AG.LND.TOTL.K2 nécessite conversion 1000 ha → km²
- **Sources** : Les champs `source` sont mis à jour par ajout, jamais écrasés
- **Logs** : Tous les scripts affichent des statistiques détaillées après import

## 🚀 Utilisation

```bash
# Activer l'environnement virtuel
source .venv/bin/activate

# Exécuter un script d'import
python3 scripts/import/import_mobile_subscriptions_complete.py
```

## 📚 Documentation

Pour plus de détails sur la stratégie d'averaging, voir : [`docs/LECON_IMPORT_MOYENNE.md`](../../docs/LECON_IMPORT_MOYENNE.md)
