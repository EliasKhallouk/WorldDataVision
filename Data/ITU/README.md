# ITU Datasets

Ce dossier contient les datasets de l'ITU (International Telecommunication Union).

## 📥 Note importante

Les fichiers de données CSV ne sont **pas versionnés** car ils sont volumineux et les données sont déjà importées dans PostgreSQL.

## 📊 Fichiers

- `individuals-using-the-internet_*.csv` - Utilisateurs Internet (non versionné)
- `Mobile-cellular subscriptions.csv` - Abonnements mobiles (non versionné)
- `Fixed-broadband subscriptions.csv` - Abonnements haut débit (non versionné)

## 🔧 Import dans la BDD

Les données sont déjà importées. Pour réimporter :

```bash
# Mobile cellular subscriptions
python3 scripts/import/import_mobile_subscriptions_complete.py

# Fixed broadband subscriptions
python3 scripts/import/import_broadband_itu.py
```

## 📈 Statistiques

### IT.CEL.SETS.P2 - Mobile cellular subscriptions
- **10,729 valeurs** (World Bank + ITU)
- **222 pays**
- Sources combinées avec averaging

### IT.NET.BBND.P2 - Fixed broadband subscriptions
- **4,337 valeurs** (World Bank + ITU)
- **212 pays**
- Sources combinées avec averaging

## 🌐 Source

[ITU Statistics](https://www.itu.int/en/ITU-D/Statistics/Pages/stat/default.aspx)

## 📚 Documentation

- [Script import mobile](../../scripts/import/import_mobile_subscriptions_complete.py)
- [Script import broadband](../../scripts/import/import_broadband_itu.py)
