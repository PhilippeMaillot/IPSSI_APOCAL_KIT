#!/usr/bin/env python3
"""
Benchmark LLM reproductible — perturbation J2 (latence de generation de quiz).

Mesure la latence END-TO-END de la generation d'un quiz (10 QCM) pour plusieurs
modeles Ollama, sur LE MEME cours de reference et LA MEME machine. Reproduit
fidelement la charge de l'app : meme prompt (system + cours tronque a
MAX_SOURCE_CHARS) et memes parametres d'appel que backend/llm/services/
ollama_client.py (stream=false, temperature=0.4, format=json).

Ne lance AUCUNE optimisation : il se contente de MESURER (mesurer avant
d'optimiser). Le rapport d'analyse est dans docs/perturbation/p2-benchmark-llm.txt.

USAGE
-----
  # 1. Demarrer Ollama et tirer les modeles a comparer
  ollama pull llama3.1:8b
  ollama pull llama3.2:3b
  ollama pull phi3:mini

  # 2. Lancer le benchmark (5 runs par modele par defaut)
  python3 scripts/benchmark_llm.py \
      --models llama3.1:8b llama3.2:3b phi3:mini \
      --runs 5 \
      --course scripts/fixtures/cours-reference.txt \
      --out scripts/results-benchmark-j2.csv

Sans --course, un cours de reference francais embarque est utilise (pour que le
benchmark reste reproductible sans fichier externe).

SORTIE
------
  - Tableau recapitulatif en console : p50 / p95 latence, tok/s, RAM observable.
  - CSV (--out) : une ligne par modele, importable dans le rapport.

Dependances : uniquement `requests` (deja dans le backend). Aucune dependance
Django : le script est autonome.
"""

import argparse
import json
import statistics
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("Le module 'requests' est requis : pip install requests")


# --- Repris a l'identique de backend/llm/services/quiz_prompt.py -------------
MAX_SOURCE_CHARS = 8000

SYSTEM_PROMPT = """Tu es un assistant pédagogique francophone spécialisé en
génération de QCM. À partir du cours fourni, tu génères exactement 10 questions
à choix multiples pour aider un étudiant à réviser.

Règles ABSOLUES :
- Exactement 10 questions.
- Chaque question a EXACTEMENT 4 options.
- Une seule bonne réponse par question, indiquée par "correct_index" (0 à 3).
- Pas de markdown, pas de balises HTML, pas d'explications hors JSON.
- Sortie = JSON STRICT et UNIQUEMENT JSON.

Format de sortie :
{
  "questions": [
    {"prompt": "...", "options": ["...","...","...","..."], "correct_index": 0},
    ... (10 entrées)
  ]
}
"""


def build_full_prompt(source_text: str, title: str) -> str:
    truncated = source_text[:MAX_SOURCE_CHARS]
    user = f"TITRE DU COURS : {title}\n\nCOURS :\n{truncated}\n\nGÉNÈRE LE JSON MAINTENANT :"
    return f"{SYSTEM_PROMPT}\n\n{user}"


# --- Cours de reference embarque (fallback si --course absent) ---------------
DEFAULT_COURSE_TITLE = "Algorithmique - Complexite et tris"
DEFAULT_COURSE = (
    "La complexite algorithmique mesure les ressources (temps, memoire) "
    "consommees par un algorithme en fonction de la taille n de l'entree. "
    "On utilise la notation de Landau (grand O). Un parcours simple d'un tableau "
    "est en O(n). Une double boucle imbriquee est en O(n^2). La recherche "
    "dichotomique dans un tableau trie est en O(log n). "
    "Le tri par insertion est en O(n^2) dans le pire cas mais O(n) sur une "
    "entree presque triee ; il est stable et en place. Le tri fusion (merge sort) "
    "est en O(n log n) dans tous les cas, stable, mais necessite O(n) memoire "
    "supplementaire. Le tri rapide (quicksort) est en moyenne O(n log n) mais "
    "O(n^2) dans le pire cas selon le choix du pivot ; il est en place mais non "
    "stable. Le tri par tas (heapsort) est O(n log n) garanti, en place, non "
    "stable. La borne inferieure des tris par comparaison est Omega(n log n). "
    "Les tris non comparatifs (comptage, radix) peuvent atteindre O(n) sous "
    "hypotheses sur les cles. La complexite spatiale distingue la memoire "
    "auxiliaire de la memoire totale. "
) * 6  # ~ quelques milliers de caracteres, proche d'un vrai chapitre


def percentile(values, p):
    """p en [0,100]. Interpolation lineaire simple."""
    if not values:
        return float("nan")
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def validate_quiz(raw: str):
    """Retourne (ok, n_questions). Validation legere : 10 questions, 4 options."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1 or end == -1:
            return False, 0
        try:
            data = json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            return False, 0
    qs = data.get("questions", []) if isinstance(data, dict) else []
    ok = len(qs) == 10 and all(len(q.get("options", [])) == 4 for q in qs)
    return ok, len(qs)


def run_once(host, model, prompt, timeout):
    """Un appel Ollama. Retourne un dict de metriques pour ce run."""
    t0 = time.perf_counter()
    resp = requests.post(
        f"{host}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.4},
            "format": "json",
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    elapsed = time.perf_counter() - t0
    data = resp.json()
    raw = data.get("response", "")
    ok, n = validate_quiz(raw)
    # Ollama renvoie des durees en nanosecondes
    eval_count = data.get("eval_count", 0)
    eval_dur_ns = data.get("eval_duration", 0) or 1
    prompt_eval = data.get("prompt_eval_count", 0)
    tok_s = eval_count / (eval_dur_ns / 1e9) if eval_count else 0.0
    return {
        "elapsed_s": elapsed,
        "valid": ok,
        "n_questions": n,
        "out_tokens": eval_count,
        "prompt_tokens": prompt_eval,
        "tok_per_s": tok_s,
    }


def main():
    ap = argparse.ArgumentParser(description="Benchmark latence LLM (perturbation J2)")
    ap.add_argument("--models", nargs="+",
                    default=["llama3.1:8b", "llama3.2:3b", "phi3:mini"])
    ap.add_argument("--runs", type=int, default=5)
    ap.add_argument("--warmup", type=int, default=1,
                    help="runs de chauffe non comptes (chargement du modele en RAM)")
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--course", default=None, help="fichier .txt du cours de reference")
    ap.add_argument("--title", default=DEFAULT_COURSE_TITLE)
    ap.add_argument("--out", default="scripts/results-benchmark-j2.csv")
    args = ap.parse_args()

    if args.course:
        with open(args.course, encoding="utf-8") as f:
            source = f.read()
    else:
        source = DEFAULT_COURSE
    prompt = build_full_prompt(source, args.title)

    print(f"Cours de reference : {args.title!r} ({len(source)} car., "
          f"tronque a {MAX_SOURCE_CHARS})")
    print(f"Machine : a renseigner dans le rapport. Runs comptes : {args.runs} "
          f"(+{args.warmup} chauffe)\n")

    rows = []
    for model in args.models:
        print(f"=== {model} ===")
        for _ in range(args.warmup):
            try:
                run_once(args.host, model, prompt, args.timeout)
            except Exception as exc:  # noqa: BLE001
                print(f"  [chauffe] echec : {exc}")
        samples = []
        for i in range(args.runs):
            try:
                r = run_once(args.host, model, prompt, args.timeout)
                samples.append(r)
                flag = "ok" if r["valid"] else f"INVALIDE({r['n_questions']}q)"
                print(f"  run {i+1}: {r['elapsed_s']:6.1f}s  "
                      f"{r['tok_per_s']:5.1f} tok/s  [{flag}]")
            except Exception as exc:  # noqa: BLE001
                print(f"  run {i+1}: ECHEC {exc}")
        if not samples:
            continue
        lat = [s["elapsed_s"] for s in samples]
        rows.append({
            "model": model,
            "runs": len(samples),
            "p50_s": round(statistics.median(lat), 1),
            "p95_s": round(percentile(lat, 95), 1),
            "min_s": round(min(lat), 1),
            "max_s": round(max(lat), 1),
            "tok_per_s": round(statistics.mean(s["tok_per_s"] for s in samples), 1),
            "valid_rate": f"{sum(s['valid'] for s in samples)}/{len(samples)}",
        })
        print()

    if not rows:
        sys.exit("Aucun resultat (Ollama injoignable ou modeles absents ?).")

    # Tableau console
    cols = ["model", "runs", "p50_s", "p95_s", "min_s", "max_s", "tok_per_s", "valid_rate"]
    print("RECAPITULATIF")
    print(" | ".join(c.ljust(12) for c in cols))
    print("-" * (15 * len(cols)))
    for r in rows:
        print(" | ".join(str(r[c]).ljust(12) for c in cols))

    # CSV
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for r in rows:
            f.write(",".join(str(r[c]) for c in cols) + "\n")
    print(f"\nCSV ecrit : {args.out}")
    print("Reporter ces chiffres MESURES dans docs/perturbation/p2-benchmark-llm.txt")


if __name__ == "__main__":
    main()
