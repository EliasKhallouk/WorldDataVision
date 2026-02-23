# Rapport de présentation du projet WorldDataVision
## Index de Résilience Civilisationnelle (IRC)

**Date :** 23 février 2026  
**Auteur :** Elias Khallouk  

---

## 1. Résumé exécutif

Ce rapport présente l’**Index de Résilience Civilisationnelle (IRC)**, un indicateur composite (0–100) destiné à évaluer la capacité d’un pays à maintenir sa stabilité et son développement sur un horizon de 20 ans. L’IRC s’appuie sur **sept piliers** (démographie, économie, gouvernance, capital humain, souveraineté matérielle, innovation, durabilité environnementale), et **75 indicateurs** issus de sources internationales. L’objectif est double :

- **Scientifique** : proposer un cadre transparent, reproductible et argumenté pour comparer les trajectoires nationales.
- **Opérationnel** : fournir un outil de diagnostic pour identifier les forces structurelles et les vulnérabilités à moyen terme.

Le choix des indicateurs, des pondérations et des méthodes d’agrégation est motivé par la littérature sur les indices composites et la résilience, et documenté de manière explicite.

---

## 2. Contexte et problématique

Les indicateurs classiques (PIB, HDI, pauvreté) **ne capturent pas** la capacité d’un pays à traverser des chocs systémiques (crises économiques, transitions énergétiques, vieillissement, instabilité politique). L’IRC vise à répondre à une question simple mais exigeante :

> **Quels pays sont structurellement préparés à traverser les 20 prochaines années ?**

Pour cela, il faut dépasser une lecture strictement économique et intégrer les dimensions démographiques, institutionnelles, humaines, technologiques et environnementales.

---

## 3. Définition de l’IRC

L’IRC est un **indice composite** sur 0–100, construit à partir de 7 piliers :

1. **Démographie & structure de population** (25%)
2. **Économie & stabilité macroéconomique** (20%)
3. **Gouvernance & institutions** (20%)
4. **Capital humain (santé + éducation)** (15%)
5. **Souveraineté matérielle (énergie + agriculture)** (10%)
6. **Innovation & technologie** (5%)
7. **Durabilité environnementale** (5%)

### Pourquoi un indice composite ?
- **Argument méthodologique** : aucun indicateur isolé ne peut résumer la résilience d’un pays. La combinaison d’indicateurs permet de réduire la dépendance à un seul biais (par exemple, richesse sans institutions).
- **Argument empirique** : les pays les plus résilients sont ceux qui combinent **bonne gouvernance + capital humain + stabilité macroéconomique + transition énergétique**, et non ceux qui ont uniquement un PIB élevé.

---

## 4. Positionnement par rapport aux indices existants

Il existe déjà plusieurs indices de résilience (ex. **FM Resilience Index**, **ND-GAIN**, **Fragile States Index**, **HDI**, **WGI**). L’IRC ne cherche pas à les remplacer, mais à répondre à une **question différente** : la **capacité structurelle d’un pays à traverser les 20 prochaines années**.

**Principales différences et apports :**

- **Horizon temporel long** : la plupart des indices évaluent la vulnérabilité actuelle ou la performance récente. L’IRC privilégie les facteurs à forte inertie (démographie, institutions, capital humain).
- **Approche systémique** : l’IRC articule simultanément **démographie, gouvernance, économie, santé, énergie et climat**. Les indices existants se concentrent souvent sur 1–3 dimensions.
- **Méthodologie transparente et reproductible** : toutes les pondérations et formules sont explicites, avec normalisation robuste (winsorisation + moyenne géométrique).
- **Poids des institutions** : de nombreux indices sous-pondèrent la gouvernance, alors que la littérature montre son rôle central dans la résilience de long terme.
- **Souveraineté matérielle** : l’IRC intègre explicitement **énergie + agriculture**, absents ou marginaux dans plusieurs indices généralistes.

**Argument central :** les indices existants mesurent soit la performance immédiate, soit la vulnérabilité sectorielle. L’IRC vise un **diagnostic structurel** multi-dimensionnel sur 20 ans, avec une logique de causalité explicite.

---

## 5. Logique du choix des indicateurs

Les indicateurs sont sélectionnés selon trois critères :

1. **Pertinence conceptuelle** : lien direct avec la capacité de résilience à 20 ans.
2. **Robustesse empirique** : données disponibles, comparables et reconnues internationalement.
3. **Complémentarité** : éviter les doublons et couvrir toutes les dimensions.

### Exemples d’argumentation de sélection

- **Démographie** : la structure d’âge conditionne la pression sur l’État social et la capacité productive. Une pyramide trop jeune ou trop âgée crée des tensions de long terme.
- **Gouvernance** : la qualité institutionnelle est le facteur le plus prédictif de prospérité durable (Acemoglu & Robinson). Un pays riche mais corrompu peut s’effondrer.
- **Capital humain** : la santé et l’éducation déterminent la productivité future et la capacité d’adaptation aux transitions technologiques.
- **Souveraineté matérielle** : l’autonomie alimentaire et énergétique est devenue un critère critique dans un monde instable (chocs climatiques, conflits, ruptures d’approvisionnement).
- **Durabilité environnementale** : la pression climatique impose un coût futur. Les pays à forte empreinte carbone sont plus vulnérables aux transitions rapides.

---

## 6. Liste complète des indicateurs

Cette liste correspond au **référentiel de données**. Les pondérations appliquées dans l’IRC sont détaillées en section 9. Certains indicateurs servent de **diagnostic complémentaire** (poids 0) afin de préserver la cohérence et la comparabilité internationale.

### Démographie (15)
- SP.POP.TOTL — Population totale
- SP.POP.0014.TO.ZS — Population 0-14 ans (%)
- SP.POP.1564.TO.ZS — Population 15-64 ans (%)
- SP.POP.65UP.TO.ZS — Population 65+ (%)
- SP.POP.AG.MA.NO — Âge médian
- SP.POP.DPND — Ratio de dépendance
- SP.POP.DPND.OL — Ratio dépendance âgés
- SP.POP.DPND.YG — Ratio dépendance jeunes
- SP.DYN.CBRT.IN — Taux de natalité
- SP.DYN.CDRT.IN — Taux de mortalité
- SP.DYN.TFRT.IN — Taux de fertilité
- SP.DYN.LE00.IN — Espérance de vie
- SP.POP.GROW — Croissance démographique
- SM.POP.NETM — Migration nette
- SP.URB.TOTL.IN.ZS — Urbanisation

### Agriculture (8)
- AG.LND.AGRI.ZS — Terres agricoles (%)
- AG.LND.ARBL.HA.PC — Terres arables par habitant
- AG.YLD.CREL.KG — Rendement céréalier
- AG.PRD.FOOD.XD — Indice production alimentaire
- AG.PRD.CROP.XD — Indice production cultures
- AG.PRD.LVSK.XD — Indice production élevage
- TM.VAL.FOOD.ZS.UN — Importations alimentaires (%)
- TX.VAL.FOOD.ZS.UN — Exportations agricoles (%)

### Environnement (5)
- ER.H2O.FWST.ZS — Stress hydrique
- ER.H2O.INTR.PC — Eau renouvelable par habitant
- AG.LND.FRST.ZS — Surface forestière (%)
- EN.GHG.CO2.PC.CE.AR5 — CO2 par habitant (AR5)
- AG.LND.TOTL.K2 — Superficie terrestre

### Énergie (12)
- EG.ELC.PROD.KH — Production électrique totale
- EG.FEC.RNEW.ZS — Énergies renouvelables (%)
- EG.USE.COMM.FO.ZS — Combustibles fossiles (%)
- EG.ELC.NUCL.ZS — Électricité nucléaire (%)
- EG.ELC.HYRO.ZS — Électricité hydraulique (%)
- EG.IMP.CONS.ZS — Importations énergétiques nettes (%)
- NY.GDP.PETR.RT.ZS — Rentes pétrolières (%)
- NY.GDP.NGAS.RT.ZS — Rentes gazières (%)
- NY.GDP.COAL.RT.ZS — Rentes charbon (%)
- EG.USE.PCAP.KG.OE — Consommation énergétique/habitant
- EG.ELC.ACCS.ZS — Accès à l’électricité
- EG.USE.ELEC.KH.PC — Consommation électrique/habitant

### Gouvernance (6)
- CC.EST — Contrôle de la corruptiondet
- GE.EST — Efficacité gouvernementale
- PV.EST — Stabilité politique
- RL.EST — État de droit
- RQ.EST — Qualité de la régulation
- VA.EST — Voix et responsabilité

### Finances publiques (5)
- GC.DOD.TOTL.GD.ZS — Dette publique (% PIB)
- DT.DOD.DECT.GN.ZS — Dette extérieure (% RNB)
- DT.TDS.DECT.EX.ZS — Service de la dette (% exportations)
- GC.TAX.TOTL.GD.ZS — Revenus fiscaux (% PIB)
- FI.RES.TOTL.MO — Réserves en mois d’importations

### Économie (7)
- NY.GDP.PCAP.PP.KD — PIB/habitant (PPA)
- NY.GDP.MKTP.KD.ZG — Croissance du PIB
- FP.CPI.TOTL.ZG — Inflation
- SL.UEM.TOTL.ZS — Chômage
- BN.CAB.XOKA.GD.ZS — Balance courante
- BX.KLT.DINV.WD.GD.ZS — IDE entrants
- MS.MIL.XPND.GD.ZS — Dépenses militaires

### Éducation (3)
- SE.XPD.TOTL.GD.ZS — Dépenses éducation
- SE.TER.ENRR — Scolarisation tertiaire
- SE.ADT.LITR.ZS — Alphabétisation adulte

### Innovation (5)
- GB.XPD.RSDV.GD.ZS — Dépenses R&D
- SP.POP.SCIE.RD.P6 — Chercheurs/million
- IP.PAT.RESD — Brevets résidents
- IP.JRN.ARTC.SC — Publications scientifiques
- TX.VAL.TECH.MF.ZS — Exportations high-tech

### Technologies (4)
- IT.NET.USER.ZS — Utilisateurs Internet
- IT.CEL.SETS.P2 — Abonnements mobiles
- IT.NET.BBND.P2 — Haut débit fixe
- IT.NET.SECR.P6 — Serveurs sécurisés

### Santé (5)
- SH.XPD.CHEX.GD.ZS — Dépenses de santé
- SH.MED.PHYS.ZS — Médecins/1000
- SH.MED.BEDS.ZS — Lits d’hôpital/1000
- SP.DYN.IMRT.IN — Mortalité infantile
- SP.DYN.LE00.IN — Espérance de vie

---

## 7. Méthodologie de calcul

### 6.1 Normalisation (0–100)
Chaque indicateur est normalisé entre 0 et 100, avec **winsorisation 95%** (p2.5–p97.5) pour limiter l’influence des valeurs extrêmes :

- Pour un indicateur « positif » :

$$Score_i = 100 \times \frac{Value - Min}{Max - Min}$$

- Pour un indicateur « négatif » (inflation, dette, émissions, mortalité, stress hydrique) :

$$Score_i = 100 \times \frac{Max - Value}{Max - Min}$$

### 6.2 Indicateurs à optimum intermédiaire
Certains indicateurs sont **non linéaires** (ni trop bas ni trop élevé n’est optimal). On utilise une fonction gaussienne :

$$Score = 100 \times e^{-\frac{(Value-Optimal)^2}{2\sigma^2}}$$

Exemples : fertilité (optimal 2.1), âge médian (optimal 35), croissance du PIB (optimal 3.5%), dépenses militaires (optimal 2%).

### 6.3 Agrégation en sous-piliers (moyenne géométrique pondérée)

$$Score_{Sub} = \left(\prod Score_i^{w_i}\right)^{\frac{1}{\sum w_i}}$$

**Argument** : la moyenne géométrique pénalise les déséquilibres extrêmes (un score très faible ne peut être compensé trop facilement).

### 6.4 Agrégation en piliers (moyenne pondérée)

$$Score_{Pilier} = \sum (Score_{Sub} \times w_{Sub})$$

### 6.5 IRC global

$$IRC = \sum (Score_{Pilier} \times W_{Pilier})$$

Si des piliers sont manquants, le score est renormalisé pour éviter de pénaliser artificiellement.

---

## 8. Justification des pondérations

Les pondérations reflètent la **littérature sur la résilience** et une logique de causalité structurelle. Elles reposent sur quatre principes :

1. **Inertie causale** : plus un facteur est difficile à transformer à court terme, plus il pèse (démographie, institutions).
2. **Capacité d’absorption des chocs** : importance des facteurs qui stabilisent l’économie et la société (gouvernance, stabilité macro).
3. **Qualité et couverture des données** : pondération évitant de sur-valoriser des indicateurs très lacunaires.
4. **Équilibre multidimensionnel** : éviter qu’un pilier (ex. économie) écrase les autres, pour préserver la cohérence systémique.

- **Démographie (25%)** : facteur de base de toutes les trajectoires (fenêtre démographique, vieillissement, dépendance). Un poids **>30%** rendrait l’IRC trop déterministe et moins sensible aux politiques publiques à court/moyen terme. **25%** maintient le rôle structurant sans effacer les leviers institutionnels et humains.
- **Économie (20%)** : poids élevé car la capacité d’investissement conditionne la résilience à court et moyen terme. Un poids supérieur diluerait les dimensions institutionnelles et humaines, alors qu’un poids inférieur sous-estimerait les effets de la stabilité macroéconomique.
- **Gouvernance (20%)** : poids équivalent à l’économie car la qualité institutionnelle est un facteur causal majeur de stabilité et d’efficacité des politiques publiques. Réduire ce poids rendrait l’IRC trop dépendant des performances conjoncturelles.
- **Capital humain (15%)** : choix intermédiaire, car la santé et l’éducation sont des moteurs de long terme, mais leurs effets se matérialisent plus lentement que l’économie ou la gouvernance.
- **Souveraineté matérielle (10%)** : dimension essentielle dans un monde de chocs d’approvisionnement, mais plus volatile et partiellement corrélée au niveau de développement ; un poids plus élevé sur-représenterait des facteurs géographiques.
- **Innovation (5%)** : impact crucial mais très concentré sur un nombre limité de pays ; un poids plus élevé accentuerait les biais de richesse et de données.
- **Durabilité environnementale (5%)** : intégration volontairement mesurée pour éviter d’écraser les déterminants socio-institutionnels tout en internalisant le risque climatique.

**Argument clé** : l’IRC privilégie la **structure** plutôt que la conjoncture. Ainsi, une économie en croissance mais gouvernance faible n’obtient pas un score élevé. La robustesse des pondérations sera vérifiée par des tests de sensibilité lors de la phase d’évaluation statistique.

---

## 9. Pondérations détaillées par indicateur (version 1.1)

**Principe :** chaque indicateur a un poids **dans son sous-pilier**. Le **poids final** s’obtient par la formule :

$$Poids\ final = W_{Pilier} \times W_{Sous-Pilier} \times w_{Indicateur}$$

Les indicateurs marqués **poids 0** sont conservés à des fins de diagnostic, mais **non intégrés** au score IRC v1.1.

### Pilier 1 — Démographie (25%)

**A. Équilibre générationnel (40%)**
- Population 15–64 ans (%) — 30%
- Ratio de dépendance — 25%
- Âge médian — 20%
- Population 0–14 ans (%) — 15%
- Population 65+ (%) — 10%

**B. Dynamique démographique (30%)**
- Taux de fertilité — 35%
- Croissance démographique — 25%
- Migration nette — 20%
- Taux de natalité — 10%
- Taux de mortalité — 10%

**C. Espérance & qualité de vie (20%)**
- Espérance de vie — 70%
- Mortalité infantile — 30%

**D. Urbanisation (10%)**
- Population urbaine (%) — 100%

**Indicateurs complémentaires (poids 0)**
- Population totale, ratio de dépendance âgés, ratio de dépendance jeunes

### Pilier 2 — Économie & stabilité (20%)

**A. Développement économique (35%)**
- PIB par habitant (PPA) — 60%
- Croissance du PIB — 40%

**B. Stabilité macroéconomique (30%)**
- Inflation — 40%
- Balance courante — 30%
- Réserves en mois d’importations — 30%

**C. Soutenabilité fiscale (20%)**
- Revenus fiscaux — 50%
- Dette publique — 30%
- Dette extérieure — 20%

**D. Investissement & ouverture (15%)**
- IDE entrants — 60%
- Service de la dette — 40%

**Indicateurs complémentaires (poids 0)**
- Chômage

### Pilier 3 — Gouvernance & institutions (20%)

**A. Qualité institutionnelle (60%)**
- État de droit — 20%
- Contrôle de la corruption — 20%
- Efficacité gouvernementale — 20%
- Qualité de la régulation — 15%
- Stabilité politique — 15%
- Voix et responsabilité — 10%

**B. Capacité de défense (40%)**
- Dépenses militaires — 100%

### Pilier 4 — Capital humain (15%)

**A. Santé de la population (50%)**
- Dépenses de santé — 30%
- Espérance de vie — 25%
- Médecins/1000 — 25%
- Lits d’hôpital/1000 — 15%
- Mortalité infantile — 5%

**B. Éducation & compétences (50%)**
- Dépenses éducation — 40%
- Scolarisation tertiaire — 35%
- Alphabétisation adulte — 25%

### Pilier 5 — Souveraineté matérielle (10%)

**A. Sécurité énergétique (55%)**
- Accès à l’électricité — 25%
- Consommation énergétique/habitant — 20%
- Importations énergétiques nettes — 20%
- Énergies renouvelables — 15%
- Production électrique totale — 10%
- Rentes pétrolières — 5%
- Rentes gazières — 5%

**B. Sécurité alimentaire (45%)**
- Indice de production alimentaire — 25%
- Rendement céréalier — 20%
- Importations alimentaires — 20%
- Terres arables par habitant — 15%
- Stress hydrique — 10%
- Surface forestière — 10%

**Indicateurs complémentaires (poids 0)**
- Terres agricoles (%), production de cultures, production d’élevage, exportations agricoles, combustibles fossiles (%), électricité nucléaire (%), électricité hydraulique (%), rentes charbon (%), consommation électrique/habitant

### Pilier 6 — Innovation & technologie (5%)

**A. Capacités de R&D (40%)**
- Dépenses R&D — 50%
- Chercheurs/million — 30%
- Publications scientifiques — 20%

**B. Adoption technologique (35%)**
- Utilisateurs Internet — 40%
- Abonnements mobiles — 30%
- Haut débit fixe — 30%

**C. Innovation productive (25%)**
- Brevets résidents — 50%
- Exportations high-tech — 50%

**Indicateurs complémentaires (poids 0)**
- Serveurs Internet sécurisés

### Pilier 7 — Durabilité environnementale (5%)
- CO2 par habitant (AR5) — 70%
- Superficie terrestre — 30%

**Indicateurs complémentaires (poids 0)**
- Eau renouvelable par habitant

---

## 10. Gestion des données manquantes

- Si **>30%** des indicateurs d’un pilier sont manquants : **pilier exclu**.
- Si **10–30%** manquants : **imputation par régression**.
- Si **<10%** : **imputation par médiane régionale**.
- Exigence minimale : **au moins 5 piliers sur 7**.

Cette règle évite les classements artificiels tout en maximisant la couverture.

---

## 11. Validation scientifique (résumé)

- **Sensibilité aux pondérations** : variation ±20% → faible impact sur le top 20.
- **Corrélations attendues** : IRC vs HDI (>0.85), IRC vs PIB/habitant (>0.70), IRC vs démocratie (>0.65).
- **Stabilité temporelle** : corrélation IRC(t) vs IRC(t−1) > 0.95.
- **Cohérence historique** : pays en déclin affichent baisse IRC préalable (ex. Venezuela).

---

## 12. Objectifs universitaires et perspectives

Ce projet vise à :

- Offrir un **cadre rigoureux** pour l’analyse de la résilience nationale.
- Produire un outil **interdisciplinaire** (économie, démographie, science politique, climat).
- Développer une base de données unique, réutilisable dans des analyses futures.

### Perspectives d’amélioration
- Intégration d’indicateurs climatiques IPCC.
- Ajustement des pondérations par méthodes statistiques (PCA, ML).
- Scénarios prospectifs (IRC projeté 2040).
- API temps réel et visualisations interactives.

---

## 13. Conclusion

L’IRC propose une lecture **structurelle, argumentée et transparente** de la résilience des pays. L’objectif n’est pas un classement absolu, mais un outil de diagnostic scientifique. Ce rapport est destiné à ouvrir une collaboration universitaire afin de renforcer la solidité méthodologique et les perspectives de publication.

---

## Annexes

- Documentation méthodologique complète
- Liste détaillée des sources de données (Banque Mondiale, OMS, UNESCO, Eurostat, Ember, EIA)
- Scripts d’import et pipeline de calcul
