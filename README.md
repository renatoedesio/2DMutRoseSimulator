# Simulador Robótico 2D

Base de um simulador top-down criado com Pygame. O robô é um círculo azul. Clique com o botão esquerdo em uma área livre para definir um destino: uma Behavior Tree valida a rota A* e a exibe em vermelho.

Os cenários podem ter vários robôs. Cada um possui rótulo, papel, rota, Blackboard e Behavior Tree próprios. Use `↑` e `↓` para alternar circularmente o robô selecionado; ele recebe um anel amarelo e é o alvo dos cliques e de `goto <sala>`.

O canto superior esquerdo mostra o local lógico identificado pela cor do pixel sob o robô. Para enviar o robô a uma sala pelo terminal em que o simulador foi iniciado, digite um comando como:

```text
goto Sala_B
```

Para enviar um robô específico sem selecioná-lo antes:

```text
goto B-1 Sala_A
```

Locais disponíveis no mapa de exemplo: `Sala_A` (azul), `Sala_B` (roxo) e `Corredor_Principal` (verde).

## Injeção de falhas

Use o botão direito do rato, ou arraste-o, para desenhar círculos pretos que se tornam obstáculos de colisão durante a execução. Se um obstáculo fechar um trecho da rota atual, a Behavior Tree invalida o contrato, interrompe o robô imediatamente e mostra `VIOLATED` no ecrã.

## Behavior Tree

A navegação utiliza `py_trees` e um Blackboard. O destino fica em `target_location`; `CheckReachability` valida a rota A* antes de `MoveToTarget` deslocar o robô. Quando não há rota, o contrato recebe o estado `VIOLATED`, o fallback interrompe o movimento e mostra o erro no ecrã.

O planejador reserva uma margem de segurança adicional junto às paredes. Assim, a rota mantém folga suficiente para o raio físico do robô, especialmente ao contornar quinas.

## Instalação

```powershell
python -m pip install -r requirements.txt
```

## Execução

Os comandos ficam organizados em `scripts/`: `scripts/manual/` contém os cenários para exploração manual e `scripts/tools/` reúne validação, execução especializada e manutenção. O comando principal é `python -m scripts`. O motor reutilizável fica em `src/core/`, os domínios em `src/domains/` e os dados de cada experimento em `experiments/`.

### Modo manual

Estes comandos abrem apenas o mapa e os robôs. A missão não é carregada automaticamente; os destinos precisam ser definidos por clique ou pelo comando `goto`:

```powershell
python -m scripts.manual.hospital_scenario_1
python -m scripts.manual.hospital_scenario_2
python -m scripts.manual.farm
```

Para consultar todos os comandos principais, execute:

```powershell
python -m scripts.help
```

O Hospital — Cenário 1 contém `A-1` e `A-2` (Limpadores), `B-1` e `B-2` (Organizadores). O Hospital — Cenário 2 contém os dois Limpadores e apenas `B-1` como Organizador.

### Modo missão automática

Para carregar uma decomposição, conectar os agentes e executar todas as tarefas do pacote visualmente, use `python -m scripts`. Por exemplo, para executar `RoomPreparation` no Hospital — Cenário 1:

```powershell
python -m scripts RoomPreparation scenario_1
```

Este é o comando correto para executar o cenário completo da missão. A opção `--validate` apenas valida o pacote e não abre a janela:

```powershell
python -m scripts RoomPreparation scenario_1 --validate
```

### Experimentos MutROSe e recuperacao

Para executar uma missao a partir de um mundo catalogado, informe o ID do
mundo com `--world`. O comando copia o XML selecionado para o World DB ativo,
executa o MutROSe, arquiva a decomposicao gerada e usa esse mesmo mundo no
simulador.

```powershell
python -m scripts --list-worlds
python -m scripts RoomPreparation scenario_1 --world AFFF_BFFV_CVVV --validate
python -m scripts RoomPreparation scenario_1 --world AFFF_BFFV_CVVV
```

As decomposicoes geradas ficam em
`mutrose/RoomPreparation/output/runs/<ID_DO_MUNDO>/task_output.json`.

Cada execucao tambem declara uma politica de recuperacao:

```powershell
python -m scripts RoomPreparation scenario_1 --world AFFF_BFFV_CVVV --recovery baseline
python -m scripts RoomPreparation scenario_1 --world AFFF_BFFV_CVVV --recovery dynamic_replanning
python -m scripts RoomPreparation scenario_1 --world AFFF_BFFV_CVVV --recovery assumption_based
```

`baseline` encerra a missao quando ocorre falha. `dynamic_replanning` marca a
falha para replanejamento pelo MutROSe. `assumption_based` marca a falha para
avaliacao pelo futuro monitor de assumptions/contratos. O dispatcher registra
em todos os casos o motivo, a tarefa e a acao que falharam.

No estado atual, as tres politicas ja sao configuraveis e o evento de falha ja
e estruturado. A etapa seguinte e o `WorldStateUpdater`: ele convertera o
estado observado apos a falha em um novo `World_db.xml`. Somente entao
`dynamic_replanning` deve chamar o MutROSe automaticamente; sem uma atualizacao
de conhecimento, o planejador receberia o mesmo mundo e poderia produzir o
mesmo plano.

## Leitura de decomposições de missão

O leitor de missões funciona fora do Pygame. Ele lê um `task_output.json`, resolve os nomes lógicos para o cenário e valida locais, papéis, capacidades e quantidade de robôs antes de qualquer execução.

```powershell
python -m scripts.tools.mission_reader "C:\caminho\para\task_output.json" hospital-1
```

Os cenários disponíveis para validação são `hospital-1`, `hospital-2` e `farm`. Os vínculos entre os nomes do JSON externo e os nomes do cenário ficam em `src/scenarios.py`. No Hospital, os nomes do World DB são usados diretamente (`RoomA`, `RoomB`, `RoomC` e `SanitizationRoom`); na Fazenda, `FarmA` é ligado a `Campo`.

Quando o experimento também tiver um World DB, valide os dois arquivos antes de executar a decomposição:

```powershell
python -m scripts.tools.mission_reader "C:\caminho\para\task_output.json" hospital-1 --world-db "C:\caminho\para\World_db.xml"
```

O cenário Hospital foi configurado conforme o exemplo de World DB: `RoomA`, `RoomB`, `RoomC` e `SanitizationRoom`. Esses nomes aparecem diretamente em `collision.png`, cada um com uma cor distinta. Para reconstruir o mapa Hospital de exemplo após uma alteração intencional, execute `python -m scripts.tools.reset_hospital_map`.

## Execução especializada do Hospital

As regras `door_open`, `is_clean` e `is_prepared` pertencem ao domínio Hospital, não ao núcleo de missões. Para executar a decomposição com essas regras e observar o estado final das salas, sem abrir o Pygame:

```powershell
python -m scripts.tools.execute_hospital_mission "C:\caminho\para\task_output.json" "C:\caminho\para\World_db.xml" hospital-1
```

O núcleo apenas ordena tarefas e ações. A especialização Hospital avalia pré-condições e aplica efeitos como abrir porta, limpar sala, sanitizar robô e mover móveis. Outros domínios, como Fazenda, podem implementar suas próprias regras sem alterar o núcleo.

## Execução visual de uma missão

As missões ficam agrupadas em pacotes autocontidos em `experiments/<experimento>/<domínio>/<cenário>/`. Cada pacote contém `task_output.json`, `World_db.xml` e `manifest.json`, evitando que uma decomposição seja usada com o mundo errado.

Para listar o catálogo:

```powershell
python -m scripts --list
```

Para executar o pacote dentro do simulador, com agentes, rotas, estados e bateria:

```powershell
python -m scripts RoomPreparation scenario_1
```

Para apenas validar o pacote sem abrir a janela, acrescente `--validate`.

Cada robô exibe seu identificador, estado e bateria. Os estados são `IDLE`, `MOVING`, `WAITING`, `ACTING` e `BLOCKED`. Durante uma ação, a bateria é consumida gradualmente; os efeitos no World State só são aplicados quando sua duração termina. Ações em grupo, como `move-furniture`, aguardam todos os robôs necessários chegarem ao local antes de começar.

## Imagens do ambiente

Cada domínio tem sua própria pasta de imagens em `src/domains/`:

- `src/domains/hospital/assets/`: arquivos do cenário Hospital.
- `src/domains/farm/assets/`: arquivos do cenário Fazenda.

Na primeira execução de um cenário, são criados `map.png` e `collision.png` nessa pasta. A máscara `collision.png` é única: preto bloqueia o robô; branco é área livre sem nome; azul, roxo e verde identificam os locais catalogados naquele cenário.

Substitua as imagens pelos seus arquivos reais, mantendo as mesmas dimensões. Para criar novas salas sem editar coordenadas, pinte-as diretamente em `collision.png` usando cores sólidas e adicione o nome/cor correspondente no cenário, em `src/scenarios.py`. Pressione `Esc` ou feche a janela para sair.
