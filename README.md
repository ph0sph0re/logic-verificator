Voici un exemple de **README** adapté à ton script Python de vérification de logique propositionnelle :

---

# Vérificateur de Logique Propositionnelle en Python

Ce projet fournit un petit outil en Python pour **parser, évaluer et vérifier des formules de logique propositionnelle**. Il permet de vérifier si des axiomes impliquent une proposition, de tester la satisfiabilité, de détecter des tautologies ou contradictions, et de trouver des contre-exemples.

---

## Fonctionnalités

* **Parser des expressions propositionnelles** avec les opérateurs :

  * `~` : négation
  * `&` : conjonction (ET)
  * `|` : disjonction (OU)
  * `->` : implication
  * `<->` : équivalence
* **Évaluation des formules** avec une valuation donnée.
* **Satisfiabilité** : vérifie si un ensemble d’axiomes est satisfiable.
* **Entailment** : vérifie si un ensemble d’axiomes implique une proposition.
* **Détection de tautologies et contradictions**.
* **Recherche de contre-exemples**.

---

## Installation

Ce projet est en **Python 3.8+** et n’a pas de dépendances externes.

1. Cloner le dépôt :

```bash
git clone <URL_DU_DEPOT>
cd <REPO>
```

2. Lancer le script directement :

```bash
python verificateur.py
```

---

## Utilisation

### Exemple simple

```python
from verificateur import parse_all, parse, is_satisfiable, entails, find_counterexample

# Définir des axiomes et une proposition
axioms_s = ["A -> B", "A"]
prop_s = "B"

# Parser les expressions
axioms = parse_all(axioms_s)
prop = parse(prop_s)

# Vérifier satisfiabilité
sat, models = is_satisfiable(axioms)
print("Axiomes satisfiables ?", sat)
if sat:
    print("Exemples de modèles:", models)

# Vérifier entailment
print("Les axiomes impliquent la proposition ?", entails(axioms, prop))

# Trouver un contre-exemple si existant
ce = find_counterexample(axioms, prop)
if ce:
    print("Contre-exemple:", ce)
else:
    print("Pas de contre-exemple trouvé.")
```

### Syntaxe des formules

* Variables : `A`, `B`, `x`, `y1`, etc.
* Parenthèses : `(` et `)`
* Négation : `~A`
* Conjonction : `A & B`
* Disjonction : `A | B`
* Implication : `A -> B`
* Équivalence : `A <-> B`

---

## Fonctions principales

* `parse(s: str) -> Expr` : Parse une chaîne en expression logique.
* `parse_all(strs: List[str]) -> List[Expr]` : Parse plusieurs chaînes.
* `is_satisfiable(axioms: List[Expr], max_models: int = 10)` : Retourne `(True/False, [modèles])`.
* `entails(axioms: List[Expr], proposition: Expr)` : Vérifie l’implication logique.
* `is_tautology(expr: Expr)` : Vérifie si l’expression est toujours vraie.
* `is_contradiction(expr: Expr)` : Vérifie si l’expression est toujours fausse.
* `find_counterexample(axioms: List[Expr], proposition: Expr)` : Retourne un contre-exemple si existant.

---

## Exemple de sortie

```
Axiomes: ['A -> B', 'A']
Proposition: B
Axiomes satisfiables ? True
Exemples de modèles: [{'A': True, 'B': True}, {'A': False, 'B': True}]
Les axiomes impliquent la proposition ? True
Pas de contre-exemple trouvé (entailment vérifié).
```

---

## Remarques

* Ce script utilise une **énumération complète des valuations** pour les modèles. Pour un grand nombre de variables, le temps de calcul peut devenir très long.
* Système conçu pour **logique propositionnelle classique**.

---

