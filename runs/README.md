# Resultados de execuções

`runs/` contém somente artefatos gerados. Cada execução deve usar um diretório
imutável e exclusivo:

```text
runs/<experiment>/<domain>/<scenario>/<run-id>/
```

Por exemplo:

```text
runs/room_preparation/hospital/scenario_1/2026-09-27T143000Z_seed-42/
```

Cada diretório de execução deve conter:

- `run_manifest.json`: identificador, seed, versões e hashes das entradas;
- `ground_truth.jsonl`: estado verdadeiro, exclusivo do avaliador;
- `evidence_reports.jsonl`: observações enviadas ao assurance core;
- `assurance_assessments.jsonl`: assessments retornados pelo core;
- `decisions.jsonl`: decisões da política de missão;
- `metrics.json`: métricas finais;
- `simulator.log`: log operacional opcional.

Os artefatos de execução são ignorados pelo Git. Os dados de entrada ficam
versionados em `experiments/` e os contratos específicos de cada cenário
ficam em `experiments/<experiment>/<domain>/<scenario>/assurance/`.
