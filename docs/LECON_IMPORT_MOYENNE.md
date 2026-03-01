# 📚 LEÇON APPRISE : Gestion des Imports de Données

**Date** : 28 février 2026  
**Contexte** : Import du taux d'alphabétisation (SE.ADT.LITR.ZS)

---

## ❌ ERREUR COMMISE

### Ce qui a été fait (INCORRECT) :
1. Import du CSV KIDB sans vérifier les données existantes
2. **REMPLACEMENT** des valeurs existantes au lieu de faire la moyenne
3. Pas de gestion des sources
4. Perte des données originales de la Banque Mondiale

### Conséquences :
- 204 valeurs écrasées
- Données originales perdues
- Sources non trackées
- Nécessité de refaire tout l'import

---

## ✅ RÈGLE D'OR : TOUJOURS FAIRE LA MOYENNE

### Principe fondamental :
**Quand une donnée existe déjà dans la base, on FAIT LA MOYENNE des deux valeurs.**

```python
# ❌ MAUVAIS (écrase les données)
cursor.execute("""
    UPDATE indicator_value
    SET value = %s
    WHERE country_id = %s AND indicator_id = %s AND year = %s
""", (new_value, country_id, indicator_id, year))

# ✅ BON (calcule la moyenne)
cursor.execute("""
    SELECT value FROM indicator_value
    WHERE country_id = %s AND indicator_id = %s AND year = %s
""", (country_id, indicator_id, year))

existing = cursor.fetchone()
if existing:
    old_value = existing[0]
    avg_value = (old_value + new_value) / 2.0
    
    cursor.execute("""
        UPDATE indicator_value
        SET value = %s, source = %s
        WHERE country_id = %s AND indicator_id = %s AND year = %s
    """, (avg_value, source, country_id, indicator_id, year))
else:
    cursor.execute("""
        INSERT INTO indicator_value (country_id, indicator_id, year, value, source)
        VALUES (%s, %s, %s, %s, %s)
    """, (country_id, indicator_id, year, new_value, source))
```

---

## 🔧 PROCESSUS DE CORRECTION APPLIQUÉ

### 1. Identification de la source originale
- Recherche dans `/Data/IRC/literacy_rate_adult.csv`
- Source : **Banque Mondiale (World Bank)**
- Format : country_code, year, value

### 2. Suppression complète
```sql
DELETE FROM indicator_value
WHERE indicator_id = (SELECT id FROM indicator WHERE code = 'SE.ADT.LITR.ZS')
```

### 3. Ré-import dans l'ordre correct

#### a) Import Banque Mondiale (données originales)
- Script : `import_world_bank_literacy.py`
- Source : `Data/IRC/literacy_rate_adult.csv`
- Résultat : ~1041 valeurs

#### b) Import KIDB (données supplémentaires)
- Script : `import_literacy_rate.py` (CORRIGÉ)
- Source : `Data/Manuel/KIDB-alphabetisation_adulte.csv`
- **Avec calcul de moyenne automatique**
- Résultat : 204 nouvelles valeurs ou moyennes

### 4. Vérification finale
- Total de valeurs : ~1245
- Sources trackées : "World Bank" et "UNESCO"
- Moyennes calculées pour les doublons

---

## 📋 CHECKLIST IMPORT DE DONNÉES

Avant tout import, vérifier :

- [ ] L'indicateur existe-t-il déjà ? (`SELECT * FROM indicator WHERE code = '...'`)
- [ ] Y a-t-il déjà des données ? (`SELECT COUNT(*) FROM indicator_value WHERE indicator_id = ...`)
- [ ] Quelle est la source des données existantes ?
- [ ] Le script gère-t-il les doublons avec **moyenne** ?
- [ ] Le script enregistre-t-il la **source** ?
- [ ] Le script a-t-il été testé sur un échantillon ?

---

## 🎯 SCRIPTS CRÉÉS

### 1. `import_world_bank_literacy.py`
Import des données de la Banque Mondiale avec gestion des moyennes et sources.

### 2. `import_literacy_rate.py` (CORRIGÉ)
Import des données KIDB avec :
- Calcul automatique de moyenne si donnée existante
- Gestion des sources (UNESCO)
- Logging des moyennes calculées

### 3. `fix_literacy_averages.py`
Script de correction pour recalculer les moyennes (archive - non utilisé car re-import complet effectué).

---

## 💡 AMÉLIORATIONS FUTURES

1. **Créer une fonction générique** `import_with_average()` réutilisable
2. **Logger toutes les opérations** dans une table d'audit
3. **Ajouter une colonne `confidence`** pour indiquer si la valeur est originale ou moyennée
4. **Créer un système de versioning** des imports

---

## ✅ VALIDATION

- [x] Données originales restaurées
- [x] Nouvelles données KIDB intégrées
- [x] Moyennes calculées pour les doublons
- [x] Sources trackées correctement
- [x] Total de valeurs cohérent (~1245)

---

**RÈGLE À NE JAMAIS OUBLIER :**
> Quand une donnée existe déjà, on fait la MOYENNE. Toujours. Sans exception.
