# ADR-0001 — Choix du backend LLM pour la génération de QCM

**Équipe 19 — EduTutor IA — APOCAL'IPSSI 2026**
**Rédacteur : Ismael CEREZO**
**Date : 30/06/2026**
**Statut : Accepté**

---

## 1. Contexte

EduTutor IA génère 10 QCM à partir d'un cours fourni par l'utilisateur (US-08).
Le kit fourni propose plusieurs backends LLM via la variable `LLM_BACKEND` :
`ollama` (local), `mock` (réponses statiques), `groq` (cloud, API gratuite).

Lors des tests du Sprint 1 (29/06/2026), le backend `ollama` avec le modèle
`llama3.1:8b` a été mesuré sur le poste de développement (CPU, sans GPU) :

| Run | Temps de génération (10 QCM) |
|-----|------------------------------|
| 1   | 2 min 47 s                   |
| 2   | 3 min 12 s                   |
| 3   | 2 min 58 s                   |
| 4   | 3 min 24 s                   |
| 5   | 2 min 51 s                   |
| **Médiane** | **2 min 58 s**     |
| **p95**     | **≈ 3 min 20 s**   |

Le critère d'acceptation de US-08 exige une génération **< 60 secondes**.
La médiane mesurée (178 s) dépasse ce seuil de **3×**.

---

## 2. Options évaluées

| Option | Latence médiane | Coût | Confidentialité | Disponibilité offline | Qualité réponses |
|--------|----------------|------|-----------------|----------------------|-----------------|
| **ollama llama3.1:8b (local CPU)** | ~3 min | Gratuit | ✅ 100% local | ✅ Oui | Bonne |
| **ollama llama3.2:3b (local CPU)** | ~60-90 s | Gratuit | ✅ 100% local | ✅ Oui | Correcte |
| **Groq API (llama3-8b-8192)** | 2-5 s | Gratuit (rate limit) | ⚠️ Données envoyées Groq | ❌ Non | Très bonne |
| **mock (réponses statiques)** | < 1 s | Gratuit | ✅ N/A | ✅ Oui | Nulle (factice) |

---

## 3. Décision

**Backend retenu : `LLM_BACKEND=groq` en développement et démo.**
**Fallback : `LLM_BACKEND=ollama` avec `llama3.2:3b` si Groq indisponible.**

Configuration `.env` :
```
LLM_BACKEND=groq
GROQ_API_KEY=<clé_équipe>
```

---

## 4. Justification

- Groq respecte le critère US-08 (< 60 s) avec une médiane de 2-5 s.
- L'API Groq est gratuite pour les petits volumes (usage pédagogique).
- Le kit dispose déjà d'un connecteur Groq intégré — zéro développement supplémentaire.
- Pour la semaine immersive, la confidentialité des données de cours n'est pas un
  critère bloquant (données fictives ou pédagogiques non sensibles).
- llama3.2:3b en fallback local permet de continuer sans réseau mais avec ~70-90 s
  de latence — acceptable pour démontrer le flux sans bloquer la démo.

**Trade-off explicite :**
Vitesse et conformité US-08 > autonomie réseau et confidentialité données.
Ce choix est réversible en production avec un GPU ou une instance Ollama distante.

---

## 5. Conséquences

- Ajouter `GROQ_API_KEY` dans `.env` (non commité, documenté dans `.env.example`).
- Documenter dans le Sprint Backlog : TASK-04 remplacée par `TASK-04b — Configurer LLM_BACKEND=groq`.
- US-08 critère "< 60 s" est satisfait avec Groq. Risque résidentiel : rate limit Groq
  en cas d'utilisation intensive simultanée (plusieurs équipes le même jour).
- Prévoir fallback `llama3.2:3b` dans le `docker compose` pour les démos hors réseau.
- ADR à revoir si un GPU est disponible en J3+ (ollama repasserait sous 10 s).

---

*Mohamed Amine EL AFRIT · APOCAL'IPSSI 2026 · CC BY-NC-SA 4.0*
