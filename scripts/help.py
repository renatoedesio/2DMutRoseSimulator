"""Mostra os comandos mais usados do Simulador 2D."""


def main() -> None:
    print(
        """
SIMULADOR ROBÓTICO 2D — AJUDA

1. Instalar as dependências (uma única vez)
   python -m pip install -r requirements.txt

2. Ver os pacotes de missão disponíveis
   python -m scripts --list

3. Validar um pacote sem abrir o simulador
   python -m scripts RoomPreparation scenario_1 --validate

4. Executar uma missão catalogada automaticamente (recomendado para experimentos)
   python -m scripts RoomPreparation scenario_1

5. Abrir apenas o mapa em modo manual (não executa uma missão)
   python -m scripts.manual.hospital_scenario_1
   python -m scripts.manual.hospital_scenario_2
   python -m scripts.manual.farm

   Para o Hospital — Cenário 1:
   - modo missão automática: python -m scripts RoomPreparation scenario_1
   - modo manual:          python -m scripts.manual.hospital_scenario_1

6. Controles na janela
   SETA CIMA / SETA BAIXO  alterna o robô selecionado
   BOTÃO ESQUERDO          envia o robô selecionado para um destino
   BOTÃO DIREITO           desenha um obstáculo temporário
   ESC                     fecha o simulador

7. Comandos no terminal durante um cenário aberto
   goto RoomA
   goto B-1 RoomB

Para consultar esta ajuda: python -m scripts.help
""".strip()
    )


if __name__ == "__main__":
    main()
