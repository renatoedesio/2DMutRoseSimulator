# Catálogo de mundos do Room Preparation

## Uso pelo simulador

Use o ID do mundo no comando principal; o XML selecionado e materializado em
`active/World_db.xml` antes da chamada ao MutROSe.

```powershell
python -m scripts --list-worlds
python -m scripts RoomPreparation scenario_1 --world AFFF_BFFV_CVVV --validate
```

O resultado e guardado em `../output/runs/<id>/task_output.json`. Sem
`--validate`, o mesmo comando abre o simulador.

## Politicas de recuperacao

`--recovery baseline` encerra apos a falha. `--recovery dynamic_replanning`
registra que a falha pede replanejamento. `--recovery assumption_based`
reserva a falha para o futuro monitor de contracts/assumptions.

As tres politicas e o evento estruturado de falha ja existem. O proximo passo
sera atualizar o World DB com o estado observado; so depois o replanejamento
automatico podera chamar o MutROSe com conhecimento novo.

`catalog.json` é a fonte legível dos estados iniciais dos cenários. Cada
identificador usa somente `RoomA`, `RoomB` e `RoomC`, nesta ordem:

```text
<sala><clean><prepared><door_open>
```

Os valores são `F` (falso) e `V` (verdadeiro). Portanto,
`AFFF_BFFV_CVVV` significa que a sala A está suja, não preparada e com a
porta fechada; a B está suja, não preparada e com a porta aberta; e a C está
limpa, preparada e com a porta aberta.

`active/World_db.xml` é o arquivo que o MutROSe lê. Para cada execução, ele
deve conter a materialização do cenário selecionado no catálogo. A sala de
sanitização não faz parte do identificador porque é infraestrutura fixa do
domínio, mas permanece declarada no catálogo e no XML.

Os XMLs de teste ficam em `scenarios/<id>/World_db.xml`. Para selecionar um
deles manualmente, copie seu conteúdo para `active/World_db.xml`; em seguida
o MutROSe pode ser executado com a mesma configuração.
