# Assurance do cenário

Este diretório contém entradas estáticas e versionadas do Mission Assurance
específicas deste cenário. Ele não contém resultados de execução.

`contract.yaml` contém uma assumption `Reachability` por tarefa. Seus limites
atuais derivam de `reachability_geometry.json`: estimativa estática de
clearance, a 95% de confiança. Eles são um baseline geométrico explícito, não
uma calibração de sensor real.

O cenário Hospital usa `meters_per_pixel = 0.01`, configurado em
`src/scenarios.py`. O sensor entrega posição em metros e `sigma_m`; a posição
verdadeira do Pygame permanece em pixels e segue exclusivamente para o logger
de ground truth.

Para derivar um limite inicial de `max_localization_uncertainty`, execute:

```powershell
python -m scripts.tools.analyze_reachability_threshold `
  experiments/room_preparation/hospital/scenario_1/task_output.json `
  experiments/room_preparation/hospital/scenario_1/World_db.xml hospital-1 `
  --output experiments/room_preparation/hospital/scenario_1/assurance/reachability_geometry.json
```

O relatório calcula o gargalo de cada rota na máscara de colisão e propõe
`sigma_max = orçamento_de_erro / k`, usando o nível de confiança informado
(`k=1,96` para 95%). Revise o resultado e sua justificativa antes de copiá-lo
para `contract.yaml`; o analisador não altera o contrato automaticamente.

`reachability_geometry.json` registra a análise inicial a 95% de confiança.
Ela estima cada rota a partir da posição inicial do robô elegível; uma futura
análise em execução deve confirmar os gargalos das rotas realmente realizadas.

O contrato deverá ser compatível com `MissionContract` do pacote `assurance` e
declarar somente assumptions, critérios e versões definidos pela pesquisa.

Não criar thresholds, assumptions ou políticas de adaptação por conveniência
da infraestrutura. Evidências, avaliações, decisões e verdade do mundo são
artefatos de uma execução e devem ser gravados em `runs/`, fora deste pacote.
