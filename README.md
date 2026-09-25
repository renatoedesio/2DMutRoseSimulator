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

Inicie o cenário desejado pelo seu próprio arquivo:

```powershell
python hospital_scenario_1.py
python hospital_scenario_2.py
python farm.py
```

O Hospital — Cenário 1 contém `A-1` e `A-2` (Limpadores), `B-1` e `B-2` (Organizadores). O Hospital — Cenário 2 contém os dois Limpadores e apenas `B-1` como Organizador.

## Imagens do ambiente

Cada cenário tem sua própria pasta em `assets/`:

- `assets/hospital/`: arquivos do cenário Hospital.
- `assets/farm/`: arquivos do cenário Fazenda.

Na primeira execução de um cenário, são criados `map.png` e `collision.png` nessa pasta. A máscara `collision.png` é única: preto bloqueia o robô; branco é área livre sem nome; azul, roxo e verde identificam os locais catalogados naquele cenário.

Substitua as imagens pelos seus arquivos reais, mantendo as mesmas dimensões. Para criar novas salas sem editar coordenadas, pinte-as diretamente em `collision.png` usando cores sólidas e adicione o nome/cor correspondente no cenário, em `src/scenarios.py`. Pressione `Esc` ou feche a janela para sair.
