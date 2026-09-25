"""Mostra os comandos mais usados do Simulador 2D."""


def main() -> None:
    print(
        """
SIMULADOR ROBÓTICO 2D — AJUDA

1. Instalar as dependências (uma única vez)
   python -m pip install -r requirements.txt

2. Ver os pacotes de missão disponíveis
   python start.py --list

3. Validar um pacote sem abrir o simulador
   python start.py RoomPreparation scenario_1 --validate

4. Executar uma missão catalogada
   python start.py RoomPreparation scenario_1

5. Abrir apenas um cenário, sem missão automática
   python hospital_scenario_1.py
   python hospital_scenario_2.py
   python farm.py

6. Controles na janela
   SETA CIMA / SETA BAIXO  alterna o robô selecionado
   BOTÃO ESQUERDO          envia o robô selecionado para um destino
   BOTÃO DIREITO           desenha um obstáculo temporário
   ESC                     fecha o simulador

7. Comandos no terminal durante um cenário aberto
   goto RoomA
   goto B-1 RoomB

Observação: no Windows, execute os comandos com a extensão .py,
por exemplo: python help.py
""".strip()
    )


if __name__ == "__main__":
    main()
